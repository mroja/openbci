#!/usr/bin/env python3

import time

import numpy as np

from obci.core.messages import Message
from obci.core.messages import protobuf_serializer
from obci.configs import variables_pb2 as proto


def proto_check(proto_name, proto_obj):
    msg_orig = Message(proto_name, 0, proto_obj)
    data = msg_orig.serialize()
    msg_deserialized = Message.deserialize(data)
    assert proto_obj == msg_deserialized.data


samples = [
    proto.Sample(timestamp=time.time(), channels=[1, 2, 3, 4, 5]),
    proto.Sample(timestamp=time.time(), channels=[1.0, 2.0, 3.0, 4.0, 5.0]),
    proto.Sample(timestamp=time.time(), channels=np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
]


def test_sample():
    for s in samples:
        proto_check('Sample', s)


def test_sample_vector():
    p = proto.SampleVector(samples=samples)
    proto_check('SampleVector', p)


if __name__ == '__main__':
    test_sample()
    test_sample_vector()
