
from obci.core.messages import Message, MessageSerializer
from obci.configs import variables_pb2 as proto


class ProtobufMessageSerializerBase(MessageSerializer):
    """
    Serializer for protobuf objects.

    Deserializer will be created dynamically using
    `gen_deserialize_func` function.
    """

    @staticmethod
    def serialize(data):
        return data.SerializeToString()

    @staticmethod
    def deserialize(data):
        raise Exception("must be implemented in derived classes")


def gen_deserialize_func(ProtoClass):
    """
    Generate deserialize for specified protobuf class.

    :param ProtoClass: protobuf class
    :return: deserializer function
    """
    def deserialize(data):
        obj = ProtoClass()
        obj.ParseFromString(data)
        return obj
    return deserialize


def generate_protobuf_serializer(proto_class):
    """
    Generate serializer for specified protobuf class.
    """
    return type('{}_{}'.format(proto_class.__name__, 'ProtobufMessageSerializer'),
                (ProtobufMessageSerializerBase,),
                {'deserialize': staticmethod(gen_deserialize_func(proto_class))})


def register_serializers() -> None:
    """
    Register serializers for all protobuf objects.
    """
    for proto_name in proto.DESCRIPTOR.message_types_by_name.keys():
        Message.register_serializer(proto_name, generate_protobuf_serializer(getattr(proto, proto_name)))


register_serializers()
