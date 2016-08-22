import asyncio
import time
import uuid
import argparse
import types
from collections import namedtuple
from typing import Optional, Callable, List, Union, Any

import zmq
import zmq.asyncio

from .message_statistics import MsgPerfStats
from .messages import Message, types as msg_types
from .asyncio_task_manager import ensure_not_inside_msg_loop
from .zmq_asyncio_task_manager import ZmqAsyncioTaskManager
from .message_handler_mixin import MessageHandlerMixin
from ..utils.zmq import bind_to_urls, recv_multipart_with_timeout

QueryDataType = Union[dict, str, int, float, type(None), List[Any]]
QueryHandler = Union[Callable[[Message], Message], Callable[[Message], types.CoroutineType]]


class PeerInitUrls(namedtuple('PeerInitUrls', ['pub_urls', 'rep_urls', 'broker_rep_url'])):
    """
    List of initial URL adresses.

    :param list pub_urls: list of PUB URL's to bind to
    :param list rep_urls: list of REP URL's to bind to
    :param str broker_rep_url: broker's REP URL
    """


class TooManyRedirectsException(Exception):
    """Raised when too many redirects occurred in Peer.query method."""


class QueryAnswerUnknown(Exception):
    """Raised when answer to query is unknown."""


class MultiplePeersAvailable(Exception):
    def __init__(self, peers: List[str], *args, **kwargs):
        """
        Raised in Peer.query method when more that one peer can answer
        specified query. Caller must decide which peer to ask and reissue query
        by calling Peer.query method with initial_peer parameter set to one of
        supplied peer.

        :param peers: list of peers
        """
        super().__init__(*args, **kwargs)
        self.peers = peers

    def __str__(self):
        return super().__str__() + ': ' + ', '.join(str(peer) for peer in self.peers)


class Peer(ZmqAsyncioTaskManager, MessageHandlerMixin):
    def __init__(self,
                 urls: Union[str, PeerInitUrls],
                 peer_id: Optional[str] = None,
                 asyncio_loop: Optional[zmq.asyncio.ZMQEventLoop] = None,
                 zmq_context: Optional[zmq.asyncio.Context] = None,
                 zmq_io_threads: int = 1,
                 hwm: int = 1000
                 ) -> None:
        """
        Base peer class. All peers derive from this class.

        :param urls: string or PeerInitUrls with initial bootstrap addresses
        :param peer_id: globally unique identifier
        :param asyncio_loop: existing ZMQ asyncio message loop or `None` if loop is requested
        :param zmq_context: existing ZMQ asyncio context or `None` if new context is requested
        :param zmq_io_threads: number of ZMQ I/O threads
        :param hwm: ZMQ high water mark
        """

        assert isinstance(urls, (str, PeerInitUrls))

        self._id = str(uuid.uuid1()) if peer_id is None else str(peer_id)

        peer_name = 'Peer_{}'.format(self.id)
        self._thread_name = peer_name
        self._logger_name = peer_name

        super().__init__(asyncio_loop, zmq_context, zmq_io_threads)

        self._initialization_finished = False

        self._hwm = hwm

        self._pub = None  # PUB socket for sending messages to broker XSUB
        self._sub = None  # SUB socket for receiving messages from broker's XPUB
        self._rep = None  # synchronous requests from peers

        self._broker_rep_url = None
        self._broker_xpub_url = None
        self._broker_xsub_url = None

        # listening URLs after binding (e.g. with specific port
        # numbers when * was given as port number or as IP address)
        self._pub_urls = []
        self._rep_urls = []
        self._pub_listening_urls = []
        self._rep_listening_urls = []

        self._query_handlers = []

        if isinstance(urls, str):
            self._ip_autodiscovery = True
            self._pub_urls = ['tcp://*:*']
            self._rep_urls = ['tcp://*:*']
            self._broker_tcp_ip_address = urls
            self._broker_rep_url = None  # TODO: fixme
        else:
            self._ip_autodiscovery = False
            assert isinstance(urls.pub_urls, (list, tuple))
            assert isinstance(urls.rep_urls, (list, tuple))
            self._pub_urls = urls.pub_urls
            self._rep_urls = urls.rep_urls
            self._broker_rep_url = urls.broker_rep_url

        # heartbeat
        self._heartbeat_enabled = False
        self._heartbeat_delay = 0.05  # 50 ms

        self._max_query_redirects = 10

        # logs verbosity
        self._log_messages = True
        self._log_peers_info = True

        # message statistics
        stats_interval = 4.0

        # async send statistics
        self._calc_send_stats = False
        self._send_stats = MsgPerfStats(stats_interval, 'SEND')

        # async receive statistics
        self._calc_recv_stats = False
        self._recv_stats = MsgPerfStats(stats_interval, 'RECV')

        self.create_task(self._connect_to_broker())

    # peer id is read only
    @property
    def id(self) -> str:
        """str: Unique identification string.

        Read only property. Can be set only when creating a new peer instance.
        """
        return self._id

    @classmethod
    def create_peer(cls, argv: List[str]) -> 'Peer':
        """Parse supplied argv and create new Peer instance."""
        parser = argparse.ArgumentParser(add_help=False)
        cls.add_arguments(parser)
        options = parser.parse_known_args(argv)[0]
        if options.broker_ip is not None:
            urls = options.broker_ip
        else:
            urls = PeerInitUrls(pub_urls=options.pub_urls,
                                rep_urls=options.rep_urls,
                                broker_rep_url=options.broker_rep_url)

        exclude_list = ['broker_ip', 'pub_urls', 'rep_urls', 'broker_rep_url']
        peer = cls(urls, **{k: v for k, v in vars(options).items()
                            if k not in exclude_list})
        return peer

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """Add command line args recognized by this class when using `create_peer` method."""
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--broker-ip')
        group.add_argument('--broker-rep-url')
        parser.add_argument('--pub-urls', nargs='+', required=False)
        parser.add_argument('--rep-urls', nargs='+', required=False)
        return parser

    @staticmethod
    def __get_filter_bytes(msg_type: str, msg_subtype: Optional[str] = None) -> bytes:
        return (msg_type + ('' if msg_subtype is None else '^' + msg_subtype)).encode('utf-8')

    def set_filter(self, msg_type: str, msg_subtype: Optional[str] = None) -> None:
        """
        Subscribe for messages with `msg_type` message type.

        Peer must be initialized to use this function.

        Args:
            msg_type:
            msg_subtype:
        """
        if self._sub is not None:
            self._sub.subscribe(self.__get_filter_bytes(msg_type, msg_subtype))

    def remove_filter(self, msg_type: str, msg_subtype: Optional[str] = None) -> None:
        """
        Unsubscribe for messages with `msg_type` message type.

        Peer must be initialized to use this function.

        Args:
            msg_type:
            msg_subtype:
        """
        if self._sub is not None:
            self._sub.unsubscribe(self.__get_filter_bytes(msg_type, msg_subtype))

    def _cleanup(self) -> None:
        """
        Close ZMQ sockets. Set initialization state to `False`.

        Note:
            Always remember to call `super()._cleanup()` when overloading this function.
        """
        self._initialization_finished = False
        self._pub.close(linger=0)
        self._sub.close(linger=0)
        self._rep.close(linger=0)
        self._pub = None
        self._sub = None
        self._rep = None
        super()._cleanup()

    async def _connect_to_broker(self) -> None:
        try:
            self._pub = self._ctx.socket(zmq.PUB)
            self._sub = self._ctx.socket(zmq.SUB)
            self._rep = self._ctx.socket(zmq.REP)
            for socket in [self._pub, self._sub, self._rep]:
                socket.set_hwm(self._hwm)
                socket.set(zmq.LINGER, 0)
            await self.__connect_to_broker_impl()
        except Exception:
            self._logger.exception("initialization failed for peer '{}': ".format(self.id))
            raise
        else:
            self._initialization_finished = True
            self.create_task(self.heartbeat())
            self.create_task(self.initialization_finished())

    async def __connect_to_broker_impl(self) -> None:
        self._pub_listening_urls = bind_to_urls(self._pub, self._pub_urls)
        self._rep_listening_urls = bind_to_urls(self._rep, self._rep_urls)

        # self._pub.connect(self._broker_xpub_url)

        if self._log_peers_info:
            msg = ("\n"
                   "Peer '{}': Initial PUB & REP bind finished.\n"
                   "PUB: {}\n"
                   "REP: {}\n"
                   "\n").format(self.id,
                                ', '.join(self._pub_listening_urls),
                                ', '.join(self._rep_listening_urls))
            self._logger.debug(msg)

        # TODO: implement self._ip_autodiscovery = True
        if self._ip_autodiscovery:
            raise Exception('self._ip_autodiscovery = True not implemented')

        # send hello to broker, receive extra URLs to bind PUB and REP sockets to
        response = await self.send_broker_message(
            Message(msg_types.BROKER_HELLO, self.id, {
                'pub_urls': self._pub_listening_urls,
                'rep_urls': self._rep_listening_urls
            }),
            timeout=30.0
        )

        self._pub_urls += response.data['extra_pub_urls']
        self._rep_urls += response.data['extra_rep_urls']

        self._pub_listening_urls += bind_to_urls(self._pub, response.data['extra_pub_urls'])
        self._rep_listening_urls += bind_to_urls(self._rep, response.data['extra_rep_urls'])

        if self._log_peers_info:
            msg = ("\n"
                   "Peer '{}': After BROKER_HELLO.\n"
                   "PUB: {}\n"
                   "REP: {}\n"
                   "\n").format(self.id,
                                ', '.join(self._pub_listening_urls),
                                ', '.join(self._rep_listening_urls))
            self._logger.debug(msg)

        # after binding PUB and REP sockets send real URLs to the broker
        # and receive broker's XPUB port to connect SUB to
        response = await self.send_broker_message(
            Message(msg_types.BROKER_REGISTER_PEER, self.id, {
                'pub_urls': self._pub_listening_urls,
                'rep_urls': self._rep_listening_urls
            }),
            timeout=30.0
        )
        self._broker_xpub_url = response.data['xpub_url']
        self._broker_xsub_url = response.data['xsub_url']

        self._sub.connect(self._broker_xpub_url)
        self._pub.connect(self._broker_xsub_url)

        if self._log_peers_info:
            msg = ("\n"
                   "Peer '{}'. Connect to Broker finished.\n"
                   "Connected to broker at REP {}; XPUB {}\n"
                   "PUB URLs: {}\n"
                   "REP URLs: {}\n"
                   "\n").format(self.id,
                                self._broker_rep_url,
                                self._broker_xpub_url,
                                ', '.join(self._pub_listening_urls),
                                ', '.join(self._rep_listening_urls))
            self._logger.info(msg)

    async def initialization_finished(self) -> None:
        """
        Run when initialization finished and all message sending mechanisms
        are available to use.
        """
        self.create_task(self._receive_sync_messages())
        self.create_task(self._receive_async_messages())

    async def heartbeat(self) -> None:
        """
        Periodically send HEARTBEAT messages.
        """
        heartbeat_message = Message(msg_types.HEARTBEAT, self.id)
        while True:
            heartbeat_timestamp = time.monotonic()
            if self._heartbeat_enabled:
                await self.send_message(heartbeat_message)
            sleep_duration = self._heartbeat_delay - (time.monotonic() - heartbeat_timestamp)
            if sleep_duration < 0:
                sleep_duration = 0
            await asyncio.sleep(sleep_duration)

    async def send_broker_message(self, msg: Message, timeout: float = 5.0) -> Message:
        """
        Send message to Broker and return answer.

        :param msg: message object to send
        :param timeout: timeout in seconds
        :return: response message
        """
        return await self.send_message_to_peer(self._broker_rep_url, msg, timeout)

    async def send_message_to_peer(self, url: str, msg: Message, timeout: float = 5.0) -> Message:
        """
        Send message to specified peer and return answer.

        :param url: peer's REP socket URL
        :param msg: message object to send
        :param timeout: timeout in seconds
        :return: response message
        """
        if self._log_messages:
            self._logger.debug("sending sync message to '{}': type '{}', subtype '{}'"
                               .format(url, msg.type, msg.subtype))
        req = self._ctx.socket(zmq.REQ)
        req.connect(url)
        try:
            await req.send_multipart(msg.serialize())
            response = await recv_multipart_with_timeout(req, timeout)
        finally:
            req.close(linger=0)
        return Message.deserialize(response)

    async def send_message(self, msg: Message) -> None:
        """
        Send broadcast message.

        :param msg: message object to send
        """
        if self._log_messages:
            self._logger.debug("sending async message: type '{}', subtype '{}'"
                               .format(msg.type, msg.subtype))
        serialized_msg = msg.serialize()
        if self._calc_send_stats:
            self._send_stats.msg(serialized_msg)
        await self._pub.send_multipart(serialized_msg)

    @ensure_not_inside_msg_loop
    def query(self,
              query_type: str,
              query_params: Optional[dict] = None,
              initial_peer: Optional[str] = None
              ) -> QueryDataType:
        """
        Send query message to Broker (or any other peer in `initial_peer` is specified).

        Returned value can be any JSON-serializable object.

        :param query_type: query type
        :param query_params: optional query parameters
        :param initial_peer: if specified this peer will be asked instead of Broker
        :return: query response
        """
        return self.create_task(self.query_async(query_type, query_params, initial_peer)).result()

    async def query_async(self,
                          query_type: str,
                          query_params: Optional[dict] = None,
                          initial_peer: Optional[str] = None
                          ) -> QueryDataType:
        """
        Async version of :func:`Peer.query`.
        """
        if query_params is None:
            query_params = {}
        query_msg = Message(query_type, self.id, query_params)
        url = self._broker_rep_url if initial_peer is None else initial_peer
        redirects = 0
        while True:
            response = await self.send_message_to_peer(url, query_msg)
            if response.type == msg_types.REDIRECT:
                urls = response.data['peers']
                assert len(urls) > 0
                if len(urls) == 1:
                    url = urls[0][1]
                elif len(urls) > 1:
                    raise MultiplePeersAvailable(urls, 'Multiple peers can answer this query')
            elif response.type == msg_types.INVALID_REQUEST or response.type == msg_types.INTERNAL_ERROR:
                raise QueryAnswerUnknown()
            else:
                return response.data
            redirects += 1
            if redirects >= self._max_query_redirects:
                self._logger.error("max redirects ({}) reached when executing query '{}'"
                                   .format(self._max_query_redirects, query_type))
                raise TooManyRedirectsException('max redirects reached')

    @ensure_not_inside_msg_loop
    def register_query_handler(self,
                               msg_type: str,
                               handler: QueryHandler) -> None:
        """
        Register callback handler for specified query type.

        `handler` function must return a valid `Message` object.

        :param msg_type: query type
        :param handler: function to execute when specified query is received
        """
        self.create_task(self.register_query_handler_async(msg_type, handler)).exception()

    async def register_query_handler_async(self,
                                           msg_type: str,
                                           handler: QueryHandler) -> None:
        """
        Async version of :func:`Peer.register_query_handler_async`.
        """
        response = await self.send_broker_message(
            Message(msg_types.BROKER_REGISTER_QUERY_HANDLER,
                    self.id, {'msg_type': msg_type}))
        if response.type != msg_types.OK:
            raise Exception('')
        self._query_handlers.append(msg_type)
        self.register_message_handler(msg_type, handler)

    @ensure_not_inside_msg_loop
    def unregister_query_handler(self, msg_type: Optional[str] = None) -> None:
        """
        Unregister callback handler for specified query type or for all query
        types if `msg_type` is `None`.

        :param msg_type:  query type
        """
        self.create_task(self.unregister_query_handler_async(msg_type)).exception()

    async def unregister_query_handler_async(self, msg_type: Optional[str] = None) -> None:
        """
        Async version of :func:`Peer.unregister_query_handler`.
        """
        response = await self.send_broker_message(
            Message(msg_types.BROKER_UNREGISTER_QUERY_HANDLER,
                    self.id, {'msg_type': msg_type}))
        if response.type != msg_types.OK:
            raise Exception('')
        if msg_type is None:
            for q_type in self._query_handlers:
                self.unregister_message_handler(q_type)
        else:
            self.unregister_message_handler(msg_type)

    async def _receive_sync_messages(self) -> None:
        async def sync_handler():
            try:
                try:
                    msg_raw = await self._rep.recv_multipart()
                    msg = Message.deserialize(msg_raw)
                    if self._log_messages:
                        self._logger.debug("received sync message: type '{}', subtype: '{}'"
                                           .format(msg.type, msg.subtype))
                    response = await self.handle_message(msg)
                    if not isinstance(response, Message):
                        raise Exception("Bad handler")
                    response = response.serialize()
                except Exception as ex:
                    response = Message(msg_types.INTERNAL_ERROR, self.id, str(ex)).serialize()
                    raise
                finally:
                    await self._rep.send_multipart(response)
            except Exception:
                self._logger.exception('Uncaught exception in sync message handler')

        await self.__receive_messages_helper(self._rep, sync_handler)

    async def _receive_async_messages(self) -> None:
        async def async_handler():
            try:
                msg = Message.deserialize(await self._sub.recv_multipart())
                if self._calc_recv_stats:
                    self._recv_stats.msg(msg)
                if self._log_messages:
                    self._logger.debug("received async message: type '{}', subtype: '{}'"
                                       .format(msg.type, msg.subtype))
                response = await self.handle_message(msg)
                if response is not None:
                    await self.send_message(response)
            except Exception:
                self._logger.exception('Uncaught exception in async message handler')

        await self.__receive_messages_helper(self._sub, async_handler)

    @staticmethod
    async def __receive_messages_helper(socket: zmq.asyncio.Socket,
                                        handler: Callable[[], types.CoroutineType]
                                        ) -> None:
        """
        Two concurrent polling loops are run (for SUB and REP) to avoid one message type processing blocking another.
        """
        poller = zmq.asyncio.Poller()
        poller.register(socket, zmq.POLLIN)
        while True:
            events = await poller.poll(timeout=100)  # timeout in milliseconds
            if socket in dict(events):
                await handler()
