#!/usr/bin/env python3

from obci.mx_legacy.multiplexer_constants import peers, types
from obci.mx_legacy.clients import BaseMultiplexerServer
from obci.configs import settings


class Filter(BaseMultiplexerServer):

    def __init__(self, addresses):
        super(Filter, self).__init__(addresses=addresses, type=peers.FILTER)

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            # self.conn.send_message(message=mxmsg.message, type=types.FILTERED_SIGNAL_MESSAGE, flush=True)
            self.no_response()


if __name__ == "__main__":
    Filter(settings.MULTIPLEXER_ADDRESSES).loop()
