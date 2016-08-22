#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time

from obci.core.broker import Broker


def run():
    if len(sys.argv) >= 3 and sys.argv[1] == 'run_multiplexer':
        addr = sys.argv[2]

        rep_urls = [addr.replace('0.0.0.0', 'tcp://*')]
        xpub_urls = ['tcp://*:200001']
        xsub_urls = ['tcp://*:200002']

        broker = Broker(rep_urls, xpub_urls, xsub_urls)

        while True:
            if False:  # TODO
                break
            time.sleep(0.1)

        broker.shutdown()
    else:
        sys.exit('Required command line args were not given.')
