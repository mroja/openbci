#!/usr/bin/python
# -*- coding: utf-8 -*-

from obci.mx_legacy.multiplexer_constants import peers
from obci.drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from obci.configs import settings
from obci.utils.openbci_logging import log_crash


class AmplifierTMSI(BinaryDriverWrapper):

    @log_crash
    def __init__(self, addresses):
        super(AmplifierTMSI, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)


if __name__ == "__main__":
    srv = AmplifierTMSI(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
