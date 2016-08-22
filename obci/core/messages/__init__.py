
import abc
import json
from typing import Any, List

from . import types


class MessageSerializer(metaclass=abc.ABCMeta):
    """
    Message serializer implements two methods `serialize` and `deserialize` to
    convert to and from bytes to desired data type.
    """

    @staticmethod
    @abc.abstractmethod
    def serialize(data: Any) -> bytes:
        raise Exception('Must be reimplemented in subclass')

    @staticmethod
    @abc.abstractmethod
    def deserialize(data: bytes) -> Any:
        raise Exception('Must be reimplemented in subclass')


class NullMessageSerializer(MessageSerializer):
    """
    Serialize data to empty (None) object.

    `deserialize` method always returns `None`.
    """

    @staticmethod
    def serialize(data):
        return b''

    @staticmethod
    def deserialize(data):
        return None


class StringMessageSerializer(MessageSerializer):
    """
    Serializes strings.
    """

    @staticmethod
    def serialize(data):
        return data.encode('utf-8')

    @staticmethod
    def deserialize(data):
        return data.decode('utf-8')


class JsonMessageSerializer(MessageSerializer):
    """
    Serializes any JSON-serializable objects.
    """

    @staticmethod
    def serialize(data):
        return json.dumps(data, ensure_ascii=True, separators=(',', ':')).encode('ascii')

    @staticmethod
    def deserialize(data):
        return json.loads(data.decode('ascii'))


class NoSerializerRegistered(Exception):
    """
    Raised when no serializer was registered for used message type.
    """


class Message:
    serializers = {}

    def __init__(self, type_id: str, subtype_id: str='', data: Any=None):
        """
        Message consists of:

        * type - can be any string
        * subtype - can be any string
        * data - deserialized message payload

        New message type must be registered using `Message.register_serializer`
        method before creating `Message` objects with such type.

        :param type_id: type of this message
        :param subtype_id: usually interpreted as sender peer ID
        :param data: message payload
        """
        super().__init__()
        self._type = str(type_id)
        self._subtype = str(subtype_id)
        self.data = data

    # type is read only
    @property
    def type(self) -> str:
        return self._type

    @property
    def subtype(self) -> str:
        return self._subtype

    @subtype.setter
    def subtype(self, val: str) -> None:
        self._subtype = str(val)

    @staticmethod
    def __get_serializer(msg_type: str):
        try:
            return Message.serializers[types.QUERY if msg_type.endswith(types.QUERY) else msg_type]
        except KeyError:
            raise NoSerializerRegistered("No serializer for '{}'.".format(msg_type))

    def serialize(self) -> List[bytes]:
        """
        Serialize to ZMQ multipart message.

        :return: ZMQ multipart message
        """
        serializer = Message.__get_serializer(self.type)
        data_bytes = serializer.serialize(self.data)
        return ['{}^{}'.format(self.type, self.subtype).encode('utf-8'), data_bytes]

    @staticmethod
    def deserialize(msg: List[bytes]) -> 'Message':
        """
        Create `Message` object from ZMQ multipart message.

        :param msg: multipart message received by ZMQ
        :return: Message object
        """
        if len(msg) != 2:
            raise Exception('Invalid message format')
        try:
            type_id, subtype_id = msg[0].decode('utf-8').split('^', maxsplit=1)
        except Exception:
            raise Exception('Invalid message format: invalid type or subtype')
        serializer = Message.__get_serializer(type_id)
        data = serializer.deserialize(msg[1])
        return Message(type_id, subtype_id, data)

    @staticmethod
    def register_serializer(msg_type: str, serializer_class) -> None:
        """
        Unregister serializer for specified message type.

        :param msg_type: message type
        :param serializer_class: class derived from MessageSerializer
        """
        Message.serializers[msg_type] = serializer_class()

    @staticmethod
    def unregister_serializer(msg_type: str) -> None:
        """
        Unregister serializer for specified message type.

        :param msg_type: message type
        """
        del Message.serializers[msg_type]

#
# serializers for predefined message types
#

Message.register_serializer(types.INVALID_REQUEST, StringMessageSerializer)
Message.register_serializer(types.INTERNAL_ERROR, StringMessageSerializer)
Message.register_serializer(types.HEARTBEAT, NullMessageSerializer)

Message.register_serializer(types.PEERS_READY, NullMessageSerializer)
Message.register_serializer(types.PEERS_READY_RECEIVED, NullMessageSerializer)

Message.register_serializer(types.OK, NullMessageSerializer)
Message.register_serializer(types.ERROR, StringMessageSerializer)

Message.register_serializer(types.QUERY, JsonMessageSerializer)
Message.register_serializer(types.REDIRECT, JsonMessageSerializer)

Message.register_serializer(types.BROKER_HELLO, JsonMessageSerializer)
Message.register_serializer(types.BROKER_HELLO_RESPONSE, JsonMessageSerializer)

Message.register_serializer(types.BROKER_REGISTER_PEER, JsonMessageSerializer)
Message.register_serializer(types.BROKER_REGISTER_PEER_RESPONSE, JsonMessageSerializer)

Message.register_serializer(types.BROKER_HEARTBEAT, JsonMessageSerializer)
Message.register_serializer(types.BROKER_HEARTBEAT_RESPONSE, JsonMessageSerializer)

Message.register_serializer(types.BROKER_REGISTER_QUERY_HANDLER, JsonMessageSerializer)
Message.register_serializer(types.BROKER_UNREGISTER_QUERY_HANDLER, JsonMessageSerializer)
