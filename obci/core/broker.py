import asyncio
import logging
import threading
from typing import List, Optional

import zmq
import zmq.asyncio

from .messages import Message, types as msg_types
from .message_handler_mixin import MessageHandlerMixin
from .peer import Peer, PeerInitUrls
from .zmq_asyncio_task_manager import ZmqAsyncioTaskManager
from ..utils.zmq import bind_to_urls


class PeerInfo:
    def __init__(self, peer_id: str, url: str):
        """
        Used by Broker to hold information about connected peers.

        :param peer_id: unique peer ID
        :param url: URL of peer REP socket
        """
        self.id = peer_id
        self.url = url


class MsgProxy:
    def __init__(self,
                 xpub_urls: List[str],
                 xsub_urls: List[str],
                 io_threads: int = 1,
                 hwm: int = 1000) -> None:
        """
        Message proxy is an integral part of Broker. It routes messages from
        multiple publishers to multiple subscribers.

        `MsgProxy` opens an XSUB socket, an XPUB socket, and binds them to
        specified IP addresses and ports. Then, all peers connect to the proxy,
        instead of to each other. By using such pattern it becomes trivial to
        add more subscribers or publishers.

        :param xpub_urls: list of URLs to bind XPUB socket to
        :param xsub_urls: list of URLs to bind XSUB socket to
        :param io_threads: size of the ZMQ threads pool to handle I/O operations
        :param hwm: High Water Mark set on all ZMQ sockets
        """
        self.ready = False
        self.xpub_listening_urls = []
        self.xsub_listening_urls = []

        self._xpub_urls = xpub_urls
        self._xsub_urls = xsub_urls
        self._io_threads = io_threads
        self._hwm = hwm
        self._ctx = zmq.Context(io_threads=self._io_threads)

        self._debug = False

        self._logger = logging.getLogger('MsgProxy')

        self._thread = threading.Thread(target=self.__run, name='MsgProxy')
        self._thread.daemon = True
        self._thread.start()

    def shutdown(self) -> None:
        """
        Shutdown message proxy. Release all associated resources.
        """
        self._ctx.term()
        self._thread.join()

    def __run(self) -> None:
        xpub = self._ctx.socket(zmq.XPUB)
        xsub = self._ctx.socket(zmq.XSUB)

        xpub.set_hwm(self._hwm)
        xsub.set_hwm(self._hwm)

        xpub.set(zmq.LINGER, 0)
        xsub.set(zmq.LINGER, 0)

        # xpub.set(zmq.XPUB_VERBOSE, 1)

        self.xpub_listening_urls = bind_to_urls(xpub, self._xpub_urls)
        self.xsub_listening_urls = bind_to_urls(xsub, self._xsub_urls)

        # TODO: get explicit list of interfaces (IP's) that socket was bound to
        # As a temporary hack: replace 0.0.0.0 by 127.0.0.1, because
        # in every sane environment binding to 0.0.0.0 implies 127.0.0.1.
        # This will limit peers that can connect to proxy to local ones,
        # but at that stage of development we can deal with it.

        if '0.0.0.0' in self.xpub_listening_urls[0]:
            self.xpub_listening_urls[0] = self.xpub_listening_urls[0].replace('0.0.0.0', '127.0.0.1')

        if '0.0.0.0' in self.xsub_listening_urls[0]:
            self.xsub_listening_urls[0] = self.xsub_listening_urls[0].replace('0.0.0.0', '127.0.0.1')

        self._logger.info("\nMsgProxy: XPUB: {}\nMsgProxy: XSUB: {}\n"
                          .format(', '.join(self.xpub_listening_urls),
                                  ', '.join(self.xsub_listening_urls)))

        self.ready = True

        try:
            if self._debug:
                poller = zmq.Poller()
                poller.register(xpub, zmq.POLLIN)
                poller.register(xsub, zmq.POLLIN)
                while True:
                    events = dict(poller.poll(1000))
                    if xpub in events:
                        message = xpub.recv_multipart()
                        self._logger.debug("[BROKER_PROXY] subscription message: %s", message)
                        xsub.send_multipart(message)
                    if xsub in events:
                        message = xsub.recv_multipart()
                        self._logger.debug("[BROKER_PROXY] publishing message: %s", message)
                        xpub.send_multipart(message)
            else:
                zmq.proxy(xsub, xpub)
        except zmq.ContextTerminated:
            self.ready = False
            xsub.close(linger=0)
            xpub.close(linger=0)


class _BrokerPeer(Peer):
    """
    Broker's internal peer.
    """
    pass


class Broker(ZmqAsyncioTaskManager, MessageHandlerMixin):

    def __init__(self,
                 rep_urls: List[str],
                 xpub_urls: List[str],
                 xsub_urls: List[str],
                 asyncio_loop: Optional[zmq.asyncio.ZMQEventLoop]=None,
                 zmq_context: Optional[zmq.asyncio.Context]=None,
                 zmq_io_threads: int=1,
                 hwm: int=1000,
                 msg_proxy_io_threads: int=1,
                 msg_proxy_hwm: int=1000
                 ) -> None:
        """
        Broker is as essential component of OpenBCI experiment. It consists of
        REP socket, XPUB/XSUB message proxy and internal peer (with ID '0').
        Every peer connects to broker on initialization and registers. Broker
        also acts as a message proxy and/or router between peers.

        :param rep_urls: list of URLs to bind REP socket to
        :param xpub_urls: list of URLs to bind message proxy XPUB socket to
        :param xsub_urls: list of URLs to bind message proxy XSUB socket to
        :param asyncio_loop: existing message loop to use or `None` if new message loop is requested
        :param zmq_context: existing ZMQ asyncio context or `None` if new context is requested
        :param zmq_io_threads: number of ZMQ I/O threads to use in broker
        :param hwm: ZMQ High Water Mark for broker
        :param msg_proxy_io_threads: number of ZMQ I/O threads to use in message proxy
        :param msg_proxy_hwm: ZMQ High Water Mark for message proxy
        """
        broker_name = 'Broker'
        self._thread_name = broker_name
        self._logger_name = broker_name

        super().__init__(asyncio_loop, zmq_context, zmq_io_threads)

        self._hwm = hwm

        self._rep = None

        self._rep_urls = rep_urls
        self._xpub_urls = xpub_urls
        self._xsub_urls = xsub_urls

        self._rep_listening_urls = []

        # run XPUB & XSUB proxy in different thread
        self._msg_proxy = MsgProxy(self._xpub_urls,
                                   self._xsub_urls,
                                   io_threads=msg_proxy_io_threads,
                                   hwm=msg_proxy_hwm)

        # built-in peer
        self._peer = None

        self._peers = {}

        # self._query_handlers are stored as follows:
        # {
        #   'msg_type_1': set([peer_1_info, peer_2_info]),
        #   'msg_type_2': set([peer_1_info, peer_2_info])
        # }
        self._query_handlers = {}

        self._log_messages = True

        self.register_message_handler(msg_types.BROKER_HELLO, self._handle_hello)
        self.register_message_handler(msg_types.BROKER_REGISTER_PEER, self._handle_register_peer)

        self.register_message_handler(msg_types.BROKER_REGISTER_QUERY_HANDLER,
                                      self._handle_register_query_handler)
        self.register_message_handler(msg_types.BROKER_UNREGISTER_QUERY_HANDLER,
                                      self._handle_unregister_query_handler)

        self.create_task(self._initialize_broker())

    async def _initialize_broker(self) -> None:
        self._rep = self._ctx.socket(zmq.REP)
        self._rep.set_hwm(self._hwm)
        self._rep.set(zmq.LINGER, 0)

        self._rep_listening_urls = bind_to_urls(self._rep, self._rep_urls)

        self._logger.info("Broker: listening on REP: {}".format(', '.join(self._rep_listening_urls)))

        # block until MsgProxy is ready
        while True:
            if self._msg_proxy.ready:
                break
            await asyncio.sleep(0.1)

        urls = PeerInitUrls(pub_urls=['tcp://127.0.0.1:*'],
                            rep_urls=['tcp://127.0.0.1:*'],
                            broker_rep_url=self._rep_listening_urls[0])
        self._peer = _BrokerPeer(peer_id='0',
                                 urls=urls,
                                 zmq_io_threads=self._zmq_io_threads,
                                 hwm=self._hwm,
                                 zmq_context=self._ctx)

        self.create_task(self._receive_and_handle_requests())

    async def _handle_hello(self, msg: Message) -> Message:
        if msg.subtype in self._peers:
            return Message(msg_types.INVALID_REQUEST, '0',
                           'Peer with such ID is already registered')
        pi = PeerInfo(peer_id=msg.subtype,
                      url=msg.data['rep_urls'][0])
        self._peers[pi.id] = pi
        return Message(
            msg_types.BROKER_HELLO_RESPONSE, '0', {
                'extra_pub_urls': [],
                'extra_rep_urls': []})

    async def _handle_register_peer(self, msg: Message) -> Message:
        if msg.subtype not in self._peers:
            return Message(msg_types.INVALID_REQUEST, '0', 'Say HELLO first!')
        # TODO: intelligently select proper xpub_url and xsub_url (in case when peer isn't local)
        return Message(
            msg_types.BROKER_REGISTER_PEER_RESPONSE, '0', {
                'xpub_url': self._msg_proxy.xpub_listening_urls[0],
                'xsub_url': self._msg_proxy.xsub_listening_urls[0]})

    async def _handle_register_query_handler(self, msg: Message) -> Message:
        if msg.subtype not in self._peers:
            return Message(msg_types.INVALID_REQUEST, '0', 'Say HELLO first!')
        peer = self._peers[msg.subtype]
        msg_type = msg.data['msg_type']
        if msg_type not in self._query_handlers:
            self._query_handlers[msg_type] = set()
            self.register_message_handler(msg_type, self.__query_message_handler)
        self._query_handlers[msg_type].add(peer)
        return Message(msg_types.OK, '0', {})

    async def _handle_unregister_query_handler(self, msg: Message) -> Message:
        if msg.subtype not in self._peers:
            return Message(msg_types.INVALID_REQUEST, '0', 'Say HELLO first!')
        peer = self._peers[msg.subtype]
        requested_msg_type = msg.data['msg_type']

        if requested_msg_type is None:
            # unregister all types for current peer
            for msg_type in self._query_handlers.keys():
                self._query_handlers[msg_type].discard(peer)
        else:
            # unregister only given msg_type for current peer
            assert requested_msg_type in self._query_handlers
            self._query_handlers[requested_msg_type].discard(peer)

        # remove msg_type entries with empty handlers list
        for msg_type, handlers in list(self._query_handlers.items()):
            if len(handlers) == 0:
                self.unregister_message_handler(msg_type)
                del self._query_handlers[msg_type]

        return Message(msg_types.OK, '0', {})

    async def __query_message_handler(self, msg: Message) -> Message:
        assert msg.type in self._query_handlers
        handlers = self._query_handlers[msg.type]
        assert len(handlers) >= 1, 'if len(handlers) == 0 there is possibly ' \
                                   'some error in handle_unregister_query_handler'
        handlers = [(pi.id, pi.url) for pi in handlers]
        return Message(msg_types.REDIRECT, '0', {'peers': handlers})

    def _cleanup(self) -> None:
        self._peer.shutdown()
        self._rep.close(linger=0)
        self._rep = None
        self._msg_proxy.shutdown()
        super()._cleanup()

    async def _receive_and_handle_requests(self) -> None:
        poller = zmq.asyncio.Poller()
        poller.register(self._rep, zmq.POLLIN)
        while True:
            events = await poller.poll(timeout=50)  # in milliseconds
            if self._rep in dict(events):
                msg = await self._rep.recv_multipart()
                try:
                    msg = Message.deserialize(msg)
                    if self._log_messages:
                        self._logger.debug('broker received message {} from {}'.format(msg.type, msg.subtype))
                    response = await self.handle_message(msg)
                    assert response is not None
                except Exception as ex:
                    response = Message(msg_types.INTERNAL_ERROR, '0', str(ex))
                    self._logger.exception('Exception during message handling in broker:')
                finally:
                    await self._rep.send_multipart(response.serialize())
