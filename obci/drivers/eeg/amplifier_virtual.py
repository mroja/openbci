#!/usr/bin/python3

from obci.mx_legacy.multiplexer_constants import peers
from obci.drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from obci.configs import settings
from obci.utils.openbci_logging import log_crash


class AmplifierVirtual(BinaryDriverWrapper):

    @log_crash
    def __init__(self, addresses):
        super(AmplifierVirtual, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

    def get_run_args(self, multiplexer_address):

        host, port = multiplexer_address
        exe = self.config.get_param('driver_executable')

        v = self.config.get_param('samples_per_packet')
        args = [exe, "-h", str(host), '-p', str(port), '-v', v]

        # if self.config.get_param("amplifier_responses"):
        #     args.extend(["-r", self.config.get_param("amplifier_responses")])
        # if self.config.get_param("dump_responses"):
        #     args.extend(["--save_responses", self.config.get_param("dump_responses")])
        return args


if __name__ == "__main__":
    srv = AmplifierVirtual(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
