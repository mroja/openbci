#!/usr/bin/env python3

import random
import time
import logging

import pytest
import zmq

from obci.core.peer import Peer
from obci.core.broker import Broker
from obci.core.messages import (Message,
                                types as msg_types,
                                NullMessageSerializer)
from obci.core.peer import PeerInitUrls

from utils import wait_for_peers


Message.register_serializer('A', NullMessageSerializer)
Message.register_serializer('B', NullMessageSerializer)
Message.register_serializer('TEST', NullMessageSerializer)
Message.register_serializer('TEST_RESPONSE', NullMessageSerializer)


class PeerWithMsgHistory(Peer):

    def __init__(self, urls, peer_id, **kwargs):
        super().__init__(urls, peer_id, **kwargs)
        self.received_messages = []
        self.register_message_handler('TEST', self.handle_test_msg)

    async def handle_test_msg(self, msg):
        self.received_messages.append(msg)
        if msg.type == 'TEST':
            return Message('TEST_RESPONSE', self._id)
        else:
            return Message(msg_types.INVALID_REQUEST, self._id, 'message type not recognized')


class SingleMessageSenderTestPeer(Peer):

    def __init__(self, urls, peer_id, msg_to_send, messages_count=1, **kwargs):
        super().__init__(urls, peer_id, **kwargs)
        self.msg_to_send = msg_to_send
        self.messages_count = messages_count
        self.sent_messages_count = 0

    async def send_messages(self):
        for _ in range(self.messages_count):
            await self.send_message(Message(self.msg_to_send, self._id))
            self.sent_messages_count += 1


class SingleMessageReceiverTestPeer(Peer):

    def __init__(self, urls, peer_id, msg_to_receive, **kwargs):
        super().__init__(urls, peer_id, **kwargs)
        self.msg_to_receive = msg_to_receive
        self.received_messages_count = 0
        self.register_message_handler(msg_to_receive, self.handle_test_message)

    async def initialization_finished(self):
        self.set_filter(self.msg_to_receive)
        await super().initialization_finished()

    async def handle_test_message(self, msg):
        if msg.type == self.msg_to_receive:
            self.received_messages_count += 1


@pytest.mark.timeout(30)
def run_connection_test(broker_rep,
                        broker_xpub,
                        broker_xsub,
                        peer_pub,
                        peer_rep):

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    urls = PeerInitUrls(pub_urls=[peer_pub],
                        rep_urls=[peer_rep],
                        broker_rep_url=broker_rep)
    peer = Peer(urls, 1)

    wait_for_peers([peer], broker)

    peer.shutdown()
    broker.shutdown()


@pytest.mark.timeout(30)
def run_connection_test_2(broker_rep,
                          broker_xpub,
                          broker_xsub,
                          peer_pub,
                          peer_rep):

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    urls = PeerInitUrls(pub_urls=[peer_pub],
                        rep_urls=[peer_rep],
                        broker_rep_url=broker_rep)
    peer1 = Peer(urls, '1')
    peer2 = Peer(urls, '2')

    wait_for_peers([peer1, peer2], broker)

    peer1.shutdown()
    peer2.shutdown()
    broker.shutdown()


def test_connection_with_specified_port():
    params = {
        'broker_rep': 'tcp://127.0.0.1:20001',
        'broker_xpub': 'tcp://127.0.0.1:20002',
        'broker_xsub': 'tcp://127.0.0.1:20003',
        'peer_pub': 'tcp://127.0.0.1:20004',
        'peer_rep': 'tcp://127.0.0.1:20005'
    }
    run_connection_test(**params)
    print('test_1 finished')


def test_connection_with_any_port():
    params = {
        'broker_rep': 'tcp://127.0.0.1:20001',
        'broker_xpub': 'tcp://127.0.0.1:20002',
        'broker_xsub': 'tcp://127.0.0.1:20003',
        'peer_pub': 'tcp://127.0.0.1:*',
        'peer_rep': 'tcp://127.0.0.1:*'
    }
    run_connection_test(**params)
    print('test_2a finished')


def test_connection_with_two_peers():
    params = {
        'broker_rep': 'tcp://127.0.0.1:20001',
        'broker_xpub': 'tcp://127.0.0.1:20002',
        'broker_xsub': 'tcp://127.0.0.1:20003',
        'peer_pub': 'tcp://127.0.0.1:*',
        'peer_rep': 'tcp://127.0.0.1:*'
    }
    run_connection_test_2(**params)
    print('test_2b finished')


def test_message_receiving():
    broker_rep = 'tcp://127.0.0.1:20001'
    broker_xpub = 'tcp://127.0.0.1:20002'
    broker_xsub = 'tcp://127.0.0.1:20003'

    peer_pub_urls = [
        'tcp://127.0.0.1:20100', 'tcp://127.0.0.1:20101',
        'tcp://127.0.0.1:20102', 'tcp://127.0.0.1:20103'
    ]
    peer_rep_urls = [
        'tcp://127.0.0.1:20200', 'tcp://127.0.0.1:30201',
        'tcp://127.0.0.1:20202', 'tcp://127.0.0.1:30203'
    ]

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    urls = PeerInitUrls(pub_urls=peer_pub_urls,
                        rep_urls=peer_rep_urls,
                        broker_rep_url=broker_rep)
    peer = PeerWithMsgHistory(urls, 1)

    wait_for_peers([peer], broker)

    ctx = zmq.Context()

    sub_sockets = [ctx.socket(zmq.SUB) for _ in range(len(peer_pub_urls))]
    req_sockets = [ctx.socket(zmq.REQ) for _ in range(len(peer_rep_urls))]

    # test async

    for url, sub in zip(peer_pub_urls, sub_sockets):
        sub.connect(url)
        sub.subscribe(b'')

    async def send_test_messages():
        await peer.send_message(Message('TEST', '1'))

    time.sleep(0.1)

    peer.create_task(send_test_messages())

    time.sleep(0.5)

    for url, sub in zip(peer_pub_urls, sub_sockets):
        msg = sub.recv_multipart()
        msg = Message.deserialize(msg)
        assert msg.type == 'TEST'
        sub.disconnect(url)

    # test sync

    for url, req in zip(peer_rep_urls, req_sockets):
        req.connect(url)
        req.send_multipart(Message('TEST', '1').serialize())
        replay = req.recv_multipart()
        msg = Message.deserialize(replay)
        assert msg.type == 'TEST_RESPONSE'
        req.disconnect(url)

    # shutdown

    for sub in sub_sockets:
        sub.close(linger=0)
    for req in req_sockets:
        req.close(linger=0)
    ctx.destroy()

    peer.shutdown()
    broker.shutdown()

    print('test_3 finished')


def test_many_peers():
    broker_rep = 'tcp://127.0.0.1:20001'
    broker_xpub = 'tcp://127.0.0.1:20002'
    broker_xsub = 'tcp://127.0.0.1:20003'

    peer_pub = 'tcp://127.0.0.1:*'
    peer_rep = 'tcp://127.0.0.1:*'

    msgs_count_a = 5
    msgs_count_b = 5

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    msg_to_send = msgs_count_a * ['A'] + msgs_count_b * ['B']
    random.shuffle(msg_to_send)

    id_counter = 1

    urls = PeerInitUrls(pub_urls=[peer_pub],
                        rep_urls=[peer_rep],
                        broker_rep_url=broker_rep)

    time.sleep(1.0)

    peers_receive_a = []
    for _ in range(msgs_count_a):
        peers_receive_a.append(SingleMessageReceiverTestPeer(urls, id_counter, msg_to_receive='A'))
        id_counter += 1

    peers_receive_b = []
    for _ in range(msgs_count_b):
        peers_receive_b.append(SingleMessageReceiverTestPeer(urls, id_counter, msg_to_receive='B'))
        id_counter += 1

    peers_senders = []
    for msg in msg_to_send:
        peers_senders.append(SingleMessageSenderTestPeer(urls, id_counter, msg_to_send=msg))
        id_counter += 1

    all_peers = peers_receive_a + peers_receive_b + peers_senders

    wait_for_peers(all_peers, broker, timeout=120.0)

    time.sleep(1.0)

    for peer in peers_senders:
        peer.create_task(peer.send_messages())

    time.sleep(1.0)

    for peer in all_peers:
        peer.shutdown()

    broker.shutdown()

    for peer in peers_senders:
        assert peer.sent_messages_count == 1

    for peer in peers_receive_a:
        # print(peer.received_messages_count)
        assert peer.received_messages_count == msgs_count_a

    for peer in peers_receive_b:
        # print(peer.received_messages_count)
        assert peer.received_messages_count == msgs_count_b

    print('test_4 finished')


if __name__ == '__main__':
    # logging.root.setLevel(logging.DEBUG)
    logging.root.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    logging.root.addHandler(console)

    test_connection_with_specified_port()
    test_connection_with_any_port()
    test_connection_with_two_peers()
    test_message_receiving()
    test_many_peers()
