#!/usr/bin/env python3

import importlib
import importlib.util
import sys
import socket
import time

from obci.configs import settings
from obci.core.peer import Peer, PeerInitUrls
from obci.mx_legacy.clients import BaseMultiplexerServer


def run_legacy_peer(cls):
    # run legacy-type peer
    cls(settings.MULTIPLEXER_ADDRESSES).loop()


def run_new_peer(cls):
    BROKER_ADDR = socket.gethostbyname(settings.MULTIPLEXER_ADDRESSES[0][0])
    broker_rep_url = 'tcp://' + BROKER_ADDR + ':' + str(settings.MULTIPLEXER_ADDRESSES[0][1])

    argv = sys.argv + ['--broker-rep-url', broker_rep_url,
                       '--pub-urls', 'tcp://*:*',
                       '--rep-urls', 'tcp://*:*']

    peer = cls.create_peer(argv)

    # wait for peer to connect to broker
    while True:
        if peer._initialization_finished:
            break
        time.sleep(0.1)

    # wait for peer to shutdown
    while True:
        if not peer._initialization_finished:
            break
        time.sleep(0.1)


def get_peer_class(peer_module_path):
    try:
        spec = importlib.util.spec_from_file_location('peer', peer_module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ImportError as ex:
        print('Could not import module! {}'.format(ex))
        sys.exit(2)

    for name, cls in module.__dict__.items():
        if cls.__class__.__name__ != 'type':
            continue

        if issubclass(cls, (Peer, BaseMultiplexerServer)):
            return cls

    return None


def run():
    try:
        peer_module_path = sys.argv[1]
    except IndexError:
        print('No Python module path for peer specified.')
        sys.exit(1)

    # remove obci_run_peer entry point from argv
    sys.argv.pop(0)

    cls = get_peer_class(peer_module_path)
    if cls is None:
        print('No peer is defined in the specified module.')
        sys.exit(2)

    if issubclass(cls, BaseMultiplexerServer):
        run_legacy_peer(cls)
    elif issubclass(cls, Peer):
        run_new_peer(cls)

    sys.exit(0)
