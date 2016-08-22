
import socket
import traceback

from obci.configs.settings import MULTIPLEXER_ADDRESSES

"""
Only two functions from this file are used around the code:
__all__ = ['connect_client', 'BaseMultiplexerServer']

connect_client and BaseMultiplexerServer are used in:

 * BaseMultiplexerServer:
   - AcquisitionControl class from OBCI2mx/obci/acquisition/acquisition_control.py
     - uses handle_message

   - ConfiguredMultiplexerServer class from OBCI2mx/obci/control/peer/configured_multiplexer_server.py
     -

   - ConfigServer from OBCI2mx/obci/control/peer/config_server.py

 * connect_client function (and therefore Client class):
   - used in self.conn in OBCI2mx/obci/control/peer/configured_client.py
     'self.conn = connect_client(addresses=addresses, type=type)'

   - used in self.conn in OBCI2mx/obci/control/peer/peer_control.py
     'self.query_conn = conn = connect_client(type=peers.CONFIGURER,
                                              addresses=settings.MULTIPLEXER_ADDRESSES)'

"""

"""
    class_<PythonClient/*, boost::shared_ptr<PythonClient>*/ >(
        "Client",
        "Client object providing Multiplexer services for python.\n"
        "Client.__init__(self, Asio_IoService, int) ->\n"
        "    construct a new object bound to the given Asio_IoService\n"
        "    of specified type\n",
        init<boost::asio::io_service&, boost::uint32_t>()
        )

    .def("_get_instance_id",    &PythonClient::instance_id)

    .def("async_connect",       (ConnectionWrapper (PythonClient::*)
                                        (const std::string&, boost::uint16_t))
                                            &PythonClient::async_connect)

    .def("connect",         (ConnectionWrapper (PythonClient::*)
                                        (const std::string&, boost::uint16_t,
                                         float)) &PythonClient::connect)

    .def("wait_for_connection", &PythonClient::wait_for_connection)
    .def("connections_count",   &PythonClient::connections_count)
    .def("shutdown",        &PythonClient::shutdown)

    .def("read_message",        &PythonClient::read_message)

    .def("schedule_one",        (ScheduledMessageTracker (PythonClient::*)
                                        (std::string))
                                            &PythonClient::schedule_one)

    .def("schedule_one",        (ScheduledMessageTracker (PythonClient::*)
                                        (std::string, ConnectionWrapper, float))
                                            &PythonClient::schedule_one)

    .def("schedule_all",        &PythonClient::schedule_all)

    .def("flush",           (void (PythonClient::*)
                                        (ScheduledMessageTracker, float) const)
                                            &PythonClient::flush)

    .def("flush_all",       &PythonClient::flush_all)

    .def("random",          &PythonClient::random64)
    ;
"""


class CppClient:
    pass


class OperationFailed(Exception):
    pass


class MxClientClient(CppClient):

    DEFAULT_TIMEOUT = 10.0
    ONE = 0
    ALL = 1

    def __init__(self, client_type):
        """initialize a client with given client (peer) type"""
        self._client_type = client_type

    def connect(self, endpoint, timeout=DEFAULT_TIMEOUT):
        """
            synchronous connect
            endpoint is e.g. ("localhost", 1980)
            return ConnectionWrapper
        """
        ip4 = socket.gethostbyname(endpoint[0])
        return super(Client, self).connect(ip4, endpoint[1], timeout)

    def wait_for_connection(self, connwrap, timeout=DEFAULT_TIMEOUT):
        """wait for connection initiated with async_connect"""
        return super(Client, self).wait_for_connection(connwrap, timeout)

    def __receive_message(self, timeout=-1):
        """
            blocking read from all the sockets (or from incoming message queue)
            returns (MultiplexerMessage, ConnectionWrapper)
        """
        next = super(Client, self).read_message(timeout)
        assert isinstance(next[0], bytes)
        mxmsg = parse_message(MultiplexerMessage, next[0])
        return (mxmsg, next[1])

    def receive_message(self, timeout=-1):
        return self.__receive_message(timeout)

    def handle_drop(self, mxmsg, connwrap=None):
        """overide in subclass if you want to get hold on every message
           dropped"""
        log(WARNING, HIGHVERBOSITY,
            text="dropping message %r" % dict(id=mxmsg.id, type=mxmsg.type,
                                              to=mxmsg.to, from_=mxmsg.from_,
                                              references=mxmsg.references, len=len(mxmsg.message))
            )

    def _check_type(self, message, type, exc=OperationFailed):
        assert isinstance(message, MultiplexerMessage)
        if message.type != type:
            raise exc()

    def _unpack(self, message, type):
        return parse_message(type, message)

    def event(self, *args, **kwargs):
        """send message through all active MX connections (arguments same as
           for send_message)"""
        return self.send_message(multiplexer=Client.ALL, *args, **kwargs)

    def query(self, message, type, timeout=DEFAULT_TIMEOUT):
        """
            Reliably ask for the response.

            Send a request `message' with type `type' through one MX
            connection.  If there is no response within `timeout' seconds,
            query all connected MX servers, to find working backend that will
            handle the request. If such a backend is found within `timeout'
            seconds, repeat the request directly to the working backend through
            the working MX connection.
        """
        assert not isinstance(message, MultiplexerMessage)
        query = self.new_message(type=type, message=message)
        first_request_delivery_errored = False
        try:
            response, connwrap = self.send_and_receive(query,
                                                       multiplexer=Client.ONE, timeout=timeout,
                                                       ignore_types=(types.REQUEST_RECEIVED,))
            if response.type != types.DELIVERY_ERROR:
                return response
            first_request_delivery_errored = True
        except OperationTimedOut:
            pass

        # find working backends
        search = BackendForPacketSearch()
        search.packet_type = type
        mxmsg = self.new_message(message=search,
                                 type=types.BACKEND_FOR_PACKET_SEARCH)
        response, connwrap = self.send_and_receive(mxmsg,
                                                   accept_ids=[query.id], multiplexer=Client.ALL, timeout=timeout,
                                                   handle_delivery_errors=True,
                                                   ignore_types=(types.REQUEST_RECEIVED,))

        if response.type == types.DELIVERY_ERROR:
            if first_request_delivery_errored:
                raise OperationFailed
            return self.receive(accept_ids=[query.id], timeout=timeout)
        if response.references == query.id:
            return response

        self._check_type(response, types.PING)

        # resent original query directly to the working backend
        direct_query = self.new_message(to=response.from_, message=message,
                                        type=type)
        assert direct_query.type == type
        assert type
        response, connwrap = self.send_and_receive(direct_query,
                                                   accept_ids=[query.id], ignore_ids=[mxmsg.id],
                                                   multiplexer=connwrap,
                                                   timeout=timeout, ignore_types=(types.REQUEST_RECEIVED,))

        if response.type == types.DELIVERY_ERROR:
            raise OperationFailed

        return response

    def send_and_receive(self, message, accept_ids=[], ignore_ids=[],
                         timeout=DEFAULT_TIMEOUT, handle_delivery_errors=False,
                         ignore_types=(), **kwargs):
        """
            Unreliably ask for the response.

            Sends a request `message' and wait until `timeout' second pass or a
            response to message or one of accept_ids is received.
        """
        timeout_ticker = TimeoutTicker(timeout)
        id, tracker = self.send_message(message, timeout=timeout_ticker(),
                                        **kwargs)
        if isinstance(tracker, ScheduledMessageTracker):
            self.flush(tracker, timeout=timeout_ticker())
        else:
            assert isinstance(tracker, int)
            assert tracker >= 0

        accept_ids = [id] + accept_ids
        while timeout_ticker.permit():
            mxmsg, connwrap = self.receive(accept_ids=accept_ids,
                                           ignore_ids=ignore_ids, ignore_types=ignore_types,
                                           timeout_ticker=timeout_ticker)
            if mxmsg.type == types.DELIVERY_ERROR and \
                    handle_delivery_errors and isinstance(tracker, int):
                # event was sent and we don't want to stop on first
                # DELIVERY_ERROR received
                tracker -= 1
                if tracker > 0:
                    continue
            return mxmsg, connwrap

        raise OperationTimedOut

    def receive(self, accept_ids, ignore_ids=[], ignore_types=(),
                timeout=DEFAULT_TIMEOUT, timeout_ticker=None):
        """
            like send_and_receive but without sending anything
        """
        if timeout_ticker is None:
            timeout_ticker = TimeoutTicker(timeout)

        while timeout_ticker.permit():
            mxmsg, connwrap = self.__receive_message(timeout=timeout_ticker())
            if mxmsg.type in ignore_types:
                continue

            if mxmsg.references in accept_ids:
                return (mxmsg, connwrap)

            if mxmsg.references not in ignore_ids:
                # unexpected message received
                log(WARNING, HIGHVERBOSITY,
                    text="message (id=%d, type=%d, from=%d, references=%d) "
                    "while waiting for reply for %r" %
                    (mxmsg.id, mxmsg.type, mxmsg.from_,
                     mxmsg.references, accept_ids)
                    )
                self.handle_drop(mxmsg, connwrap)

        raise OperationTimedOut()

    def send_message(self, message, **kwargs):
        """
            sends a message through one or more MX servers; usually
            non-blocking

            returns (message_id, message_tracker)

            :Parameters:
                - `message`: MultiplexerMessage or something that will become a
                  message body (string, PorotocolBuffer Message) (if embed is
                  True, message will become final message's body without
                  checking types)
                - `embed`: (keyword-only) force creating new
                  MultiplexerMessage, don't check `message' type
                - `multiplexer`: (keyword-only) [ ONE | ALL | Connwrap ] -- use
                  specific (set of) MX, default = ONE
                - `flush`: (keyword-only) wait until message is passed to the
                  socket layer (kernel)
                - `timeout`: (keyword-only) timeout
                - `kwargs`: will be used in construting MultiplexerMessage
                  where `embed' or message is not instance of
                  MultiplexerMessage
        """
        return self.__send_message(message, **kwargs)

    def __send_message(self, message, embed=False, multiplexer=ONE,
                       flush=False, timeout=DEFAULT_TIMEOUT, **kwargs):

        timeout_ticker = TimeoutTicker(timeout)

        if embed or not isinstance(message, MultiplexerMessage):
            mxmsg = self.new_message(message=message, **kwargs)
        else:
            mxmsg = message

        raw = mxmsg.SerializeToString()

        if multiplexer is Client.ONE:
            tracker = self.schedule_one(raw)
        elif multiplexer is Client.ALL:
            tracker = self.schedule_all(raw)
        elif isinstance(multiplexer, ConnectionWrapper):
            tracker = self.schedule_one(raw, multiplexer, timeout_ticker())
        else:
            raise NotImplementedError("selecting multiplexer with %r is not supported" %
                                      multiplexer)

        # handle flush
        if flush and tracker is not None:
            if multiplexer is Client.ALL:
                raise NotImplementedError("Flushing when sending to multiple peers is "
                                          "not implemented.")
            self.flush(tracker, timeout=timeout_ticker())

        return (mxmsg.id, tracker)

    def flush(self, tracker, timeout=DEFAULT_TIMEOUT):
        """ensure that message tracked by tracker is either sent or dropped"""
        super(Client, self).flush(tracker, timeout)

    """
    def flush_all(self, timeout=DEFAULT_TIMEOUT):
        ""try to empty all outgoing messages buffers within timeout seconds""
        super(Client, self).flush_all(timeout)
    """

    def read_message(self, *args, **kwargs):
        """shortcut for receiving a message and ingoring connection used"""
        return self.receive_message(*args, **kwargs)[0]

    # helper functions
    def random(self):
        """returns random uint64"""
        return super(Client, self).random()

    message_defaults = {}

    def new_message(self, **kwargs):
        """creates new MultiplexerMessage with some predefined values"""
        if self.message_defaults:
            kwargs = dict(self.message_defaults, **kwargs)

        # defaults
        kwargs.setdefault('id', self.random())
        kwargs.setdefault('from', self.instance_id)

        # special handling of some values

        if 'message' in kwargs and not isinstance(kwargs['message'], bytes):
            if isinstance(kwargs['message'], str):
                raise Exception('message must be a binary string')
            kwargs['message'] = kwargs['message'].SerializeToString()

        return make_message(MultiplexerMessage, **kwargs)


class BasicClient(MxClientClient):

    # TODO consider inclusion of this functionality in mxclient.Client

    def receive_message(self, *args, **kwargs):
        """wrapper around mxclient.Client.send_and_receive"""
        mxmsg, connwrap = super().receive_message(*args, **kwargs)
        return mxmsg, connwrap

    def query(self, *args, **kwargs):
        mxmsg = super(BasicClient, self).query(*args, **kwargs)
        return mxmsg

    def send_and_receive(self, *args, **kwargs):
        kwargs.setdefault('ignore_function',
                          lambda mxmsg, connwrap: mxmsg.type == types.REQUEST_RECEIVED)
        return super().send_and_receive(*args, **kwargs)


class Client(BasicClient):

    def __init__(self, addresses=MULTIPLEXER_ADDRESSES, type=None):
        # arguments are in this order to preserve compatibility
        if type is None:
            raise ValueError
        super().__init__(type)
        for host, port in addresses:
            self.connect((host, port))


def connect_client(*args, **kwargs):
    return Client(*args, **kwargs)


class MultiplexerPeer:

    def __init__(self, addresses=MULTIPLEXER_ADDRESSES, type=None):
        """Constructor.

        :Parameters:
            host
                Host of multiplexer.
            addresses
                list of (host, port) pairs
            type : multiplexer.multiplexer_constants.peers.* constant
                Type of client to create
        """
        if type is None:
            raise ValueError("no type provided")
        self.type = type
        self.conn = BasicClient(self.type)
        for (host, port) in addresses:
            self.conn.connect((host, port))


class BaseMultiplexerServer(MultiplexerPeer):
    """Abstract multiplexer server functionality."""

    # time when the instance was initilized
    _start_time = None

    def __init__(self, addresses=MULTIPLEXER_ADDRESSES, type=None):
        """
            Constructor.
            See docstring for MultiplexerPeer.__init__ for meaning of
            parameters.
        """
        super(BaseMultiplexerServer, self).__init__(addresses, type)
        self.working = True
        self.last_mxmsg = None
        self._start_time = time.time()

    start_time = property(lambda self: self._start_time,
                          doc="Time when the instance was instantiated")

    def loop(self):
        """Serve forever."""
        while self.working:
            self.last_mxmsg, self.last_connwrap = self.conn.receive_message()
            self.__handle_message()

    serve_forever = loop

    def __handle_message(self):
        try:
            self._has_sent_response = False
            if self._is_private_message(self.last_mxmsg):
                self._handle_message(self.last_mxmsg)
            else:
                self.handle_message(self.last_mxmsg)
            if not self._has_sent_response:
                log(WARNING, LOWVERBOSITY, text="handle_message() "
                    "finished w/o exception and w/o any response")

        except Exception as e:
            # report exception
            traceback.print_exc()
            if not self._has_sent_response:
                log(DEBUG, MEDIUMVERBOSITY, text=lambda: "sending "
                    "BACKEND_ERROR notification for Exception %s" % e)
                self.report_error(message=str(e))
            handled = self.exception_occurred(e)
            if not handled:
                raise

    def handle_message(self, mxmsg):
        """This method should be overriden in child classes."""
        raise NotImplementedError()

    def _is_private_message(self, mxmsg):
        """This method may be overriden in subclass to enable
        handling of private but not mx-specific messages"""
        return False

    def _handle_message(self, mxmsg):
        """This method should be overriden in subclass (also:
        _is_private_message()). Handling of private but not mx-specific
        messages."""
        raise NotImplementedError()

    def parse_message(self, type, mxmsg=None):
        """parse mxmsg.message with new Protobuf message of type `type'"""
        return parse_message(type,
                             self.last_mxmsg.message if mxmsg is None else mxmsg.message)

    """
    def notify_start(self):
        assert not self._has_sent_response, "If you use notify_start(), " \
                "place it as a first function in your handle_message() code"
        self.send_message(
                message="",
                type=types.REQUEST_RECEIVED,
                # references, workflow -- set by send_message
            )
        self._has_sent_response = False
    """

    def send_message(self, **kwargs):
        if self.last_mxmsg is not None:
            self._has_sent_response = True
            kwargs.setdefault('multiplexer', self.last_connwrap)
            kwargs.setdefault('references', self.last_mxmsg.id)
            kwargs.setdefault('workflow', self.last_mxmsg.workflow)
            kwargs.setdefault('to', self.last_mxmsg.from_)
        return self.conn.send_message(**kwargs)

    def no_response(self):
        self._has_sent_response = True

    def close(self):
        """In case we ever what to finish."""
        self.conn.shutdown()
        self.conn = None

__all__ = ['connect_client', 'BaseMultiplexerServer']
