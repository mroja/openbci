#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

from obci.mx_legacy.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings


class OBCILogCollector(ConfiguredMultiplexerServer):

    def __init__(self, addresses):
        self.socket = None
        super(OBCILogCollector, self).__init__(addresses=addresses,
                                               type=peers.OBCI_LOG_COLLECTOR)
        self.ip = '127.0.0.1'
        self.port = int(self.get_param('port'))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ready()

    def handle_message(self, mxmsg):
        if self.socket is None:
            self.no_response()
            return

        if mxmsg.type == types.OBCI_LOG_MESSAGE:
            self.logger.debug("obci collector - GOT log, sending to socket...")
            try:
                self.socket.sendto(mxmsg.message,
                                   (self.ip, self.port))
            except Exception as l_exc:
                self.logger.error("An error occured while sending log to socket")
                self.socket.close()
        else:
            self.logger.warning("Warning! unrecognised message type " + str(mxmsg.type))
        self.no_response()


if __name__ == '__main__':
    OBCILogCollector(settings.MULTIPLEXER_ADDRESSES).loop()
