#!/usr/bin/env python3

import numpy

from obci.mx_legacy.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash


class AveragingPeer(ConfiguredMultiplexerServer):

    @log_crash
    def __init__(self, addresses):
        super().__init__(addresses=addresses, type=peers.STREAM_RECEIVER)
        self._manage_params()
        self.ready()

    def _manage_params(self):
        self.input_mx_type = types.__dict__[self.config.get_param("input_mx_type")]
        self.output_mx_type = types.__dict__[self.config.get_param("output_mx_type")]

    def handle_message(self, mxmsg):
        if mxmsg.type == self.input_mx_type:
            msg = mxmsg.message
            input = variables_pb2.SampleVector()
            input.ParseFromString(msg)
            output = variables_pb2.SampleVector()
            for i_sample in input.samples:
                o_sample = output.samples.add()
                o_sample.channels.append(numpy.mean(i_sample.channels))
                o_sample.timestamp = i_sample.timestamp
            self.conn.send_message(message=output, type=self.output_mx_type, flush=True)
        self.no_response()

if __name__ == "__main__":
    AveragingPeer(settings.MULTIPLEXER_ADDRESSES).loop()
