#!/usr/bin/env python3

import pytest

from obci.core.messages import (Message,
                                types as msg_types,
                                NullMessageSerializer,
                                StringMessageSerializer,
                                JsonMessageSerializer,
                                NoSerializerRegistered)

from utils import strings_list, json_data


Message.register_serializer('NULL', NullMessageSerializer)
Message.register_serializer('STRING', StringMessageSerializer)
Message.register_serializer('JSON', JsonMessageSerializer)


def check_round_trip(msg_type, subtype, payload):
    msg = Message(msg_type, subtype, payload)
    assert isinstance(msg.type, str)
    assert isinstance(msg.subtype, str)
    msg_serialized = msg.serialize()
    assert all(isinstance(x, bytes) for x in msg_serialized)
    msg_deserialized = Message.deserialize(msg_serialized)
    assert msg_deserialized.type == msg.type
    assert msg_deserialized.subtype == msg.subtype
    if msg.data is None or isinstance(msg.data, (str, bytes, dict)):
        assert msg_deserialized.data == msg.data
    else:
        raise Exception("don't know how to compare playloads for equality")
    return True


def test_1():
    msg = Message('STRING', 123, 'abc')

    with pytest.raises(AttributeError):
        msg.type = 'NULL'

    assert msg.subtype == '123'
    msg.subtype = 321
    assert msg.subtype == '321'

    msg.data = 'cba'
    assert msg.data == 'cba'

    msg.data = 123
    assert msg.data == 123

    msg.data = None
    assert msg.data is None


def test_2():
    assert check_round_trip('NULL', 0, None)
    assert check_round_trip('NULL', '0', None)
    assert check_round_trip('NULL', 123, None)
    assert check_round_trip('NULL', '123', None)

    for s in strings_list:
        assert check_round_trip('STRING', 0, s)

    assert check_round_trip('JSON', 0, json_data)

    assert check_round_trip('QUERY', 0, json_data)

    for s in strings_list:
        assert check_round_trip(msg_types.REDIRECT, 0, s)

    assert check_round_trip('1_QUERY', 0, json_data)
    assert check_round_trip('2_QUERY', 0, json_data)
    assert check_round_trip('A_QUERY', 0, json_data)
    assert check_round_trip('B_QUERY', 0, json_data)
    assert check_round_trip('1_A_QUERY', 0, json_data)
    assert check_round_trip('1_B_QUERY', 0, json_data)
    assert check_round_trip('XYZ_QUERY', 0, json_data)
    assert check_round_trip('123_XYZ_QUERY', 0, json_data)

    with pytest.raises(NoSerializerRegistered):
        assert check_round_trip('QUERY_1', 0, json_data)
    with pytest.raises(NoSerializerRegistered):
        assert check_round_trip('QUERY_A', 0, json_data)
    with pytest.raises(NoSerializerRegistered):
        assert check_round_trip('QUERY_XYZ', 0, json_data)

    Message.unregister_serializer('NULL')
    Message.unregister_serializer('STRING')
    Message.unregister_serializer('JSON')

    with pytest.raises(NoSerializerRegistered):
        assert check_round_trip('NULL', 0, None)
    with pytest.raises(NoSerializerRegistered):
        assert check_round_trip('STRING', 0, '')
    with pytest.raises(NoSerializerRegistered):
        assert check_round_trip('JSON', 0, json_data)


if __name__ == '__main__':
    test_1()
    test_2()
