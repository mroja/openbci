
import time
import logging

from obci.core.peer import PeerInitUrls
from obci.core.broker import Broker

from obci.peers.test.dummy_amplifier import DummyAmplifierPeer
from obci.peers.test.dummy_signal_receiver import DummySignalReceiverPeer
from obci.peers.test.dummy_signal_verifier import DummySignalVerifierPeer

from utils import wait_for_peers


def run_test(broker_rep,
             broker_xpub,
             broker_xsub,
             peer_pub,
             peer_rep):

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    urls = PeerInitUrls(pub_urls=[peer_pub],
                        rep_urls=[peer_rep],
                        broker_rep_url=broker_rep)

    generator_peer = DummyAmplifierPeer(urls, 'Generator')
    receiver_peer = DummySignalReceiverPeer(urls, 'Receiver')
    verifier_peer = DummySignalVerifierPeer(urls, 'Verifier')
    all_peers = [generator_peer, receiver_peer, verifier_peer]

    wait_for_peers(all_peers, broker)

    # run for 5 seconds
    time.sleep(5.0)

    try:
        assert verifier_peer.signal_ok is True
    finally:
        verifier_peer.shutdown()
        receiver_peer.shutdown()
        generator_peer.shutdown()
        broker.shutdown()


def test_dummy_amplifier():
    params = {
        'broker_rep': 'tcp://127.0.0.1:20001',
        'broker_xpub': 'tcp://127.0.0.1:20002',
        'broker_xsub': 'tcp://127.0.0.1:20003',
        'peer_pub': 'tcp://127.0.0.1:*',
        'peer_rep': 'tcp://127.0.0.1:*'
    }
    run_test(**params)
    print('test finished')


if __name__ == '__main__':
    # logging.root.setLevel(logging.DEBUG)
    logging.root.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    logging.root.addHandler(console)

    test_dummy_amplifier()
