#!/usr/bin/env python3

import time
import logging

import pytest

from obci.core.peer import Peer
from obci.core.broker import Broker
from obci.core.peer import PeerInitUrls

from utils import wait_for_peers


@pytest.mark.timeout(30)
def run_connection_test(broker_rep,
                        broker_xpub,
                        broker_xsub,
                        peer_pub,
                        peer_rep):

    urls = PeerInitUrls(pub_urls=[peer_pub],
                        rep_urls=[peer_rep],
                        broker_rep_url=broker_rep)
    peer = Peer(urls, 1)

    time.sleep(2.0)

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    wait_for_peers([peer], broker)

    peer.shutdown()
    broker.shutdown()


def test_wait_for_broker():
    params = {
        'broker_rep': 'tcp://127.0.0.1:20001',
        'broker_xpub': 'tcp://127.0.0.1:20002',
        'broker_xsub': 'tcp://127.0.0.1:20003',
        'peer_pub': 'tcp://127.0.0.1:*',
        'peer_rep': 'tcp://127.0.0.1:*'
    }
    run_connection_test(**params)
    print('test finished')


if __name__ == '__main__':
    # logging.root.setLevel(logging.DEBUG)
    logging.root.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    logging.root.addHandler(console)

    test_wait_for_broker()
