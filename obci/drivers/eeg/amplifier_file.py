#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue
import time

from obci.mx_legacy.multiplexer_constants import peers
from obci.drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from obci.configs import settings
from obci.drivers.eeg import tags_to_mxmsg
from obci.analysis.obci_signal_processing.signal import read_info_source
from obci.analysis.obci_signal_processing.tags import read_tags_source
from obci.acquisition.acquisition_helper import get_file_path


class AmplifierFile(BinaryDriverWrapper):

    def __init__(self, addresses):
        super(AmplifierFile, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

    def _init_got_configs(self):
        self._init_files()
        self._init_configs()

    def _init_files(self):
        self.f_data = get_file_path(self.config.get_param('data_file_dir'),
                                    self.config.get_param('data_file_name') + '.obci.raw')

        i_dir = self.config.get_param('info_file_dir')
        if len(i_dir) == 0:
            i_dir = self.config.get_param('data_file_dir')
        i_name = self.config.get_param('info_file_name')
        if len(i_name) == 0:
            i_name = self.config.get_param('data_file_name')
        self.f_info = get_file_path(i_dir, i_name + '.obci.xml')

        t_dir = self.config.get_param('tags_file_dir')
        if len(t_dir) == 0:
            t_dir = self.config.get_param('data_file_dir')
        t_name = self.config.get_param('tags_file_name')
        if len(t_name) == 0:
            t_name = self.config.get_param('data_file_name')
        self.f_tags = get_file_path(t_dir, t_name + '.obci.tag')

    def _init_configs(self):
        mgr = read_info_source.FileInfoSource(self.f_info)

        names = mgr.get_param('channels_names')
        type = mgr.get_param('sample_type').lower()
        self.all_types = ';'.join([type] * len(names))
        self.all_names = ';'.join(names)
        self.all_gains = ';'.join(mgr.get_param('channels_gains'))
        self.all_offsets = ';'.join(mgr.get_param('channels_offsets'))
        self.sleep_on_out = 1.0 / float(mgr.get_param('sampling_frequency'))

        self.config.set_param('sample_type', mgr.get_param('sample_type'))
        self.config.set_param('sampling_rate', str(int(float(mgr.get_param('sampling_frequency')))))
        self.config.set_param('channel_names', self.all_names)
        if len(self.config.get_param('active_channels')) == 0:
            self.config.set_param('active_channels', self.config.get_param('channel_names'))

    def get_run_args(self, multiplexer_address):
        args = super(AmplifierFile, self).get_run_args(multiplexer_address)

        args.extend(
            ['-f', self.f_data,
             '-t', self.all_types,
             '-n', self.all_names,
             '-g', self.all_gains,
             '-o', self.all_offsets,
             '-s', self.get_param('sampling_rate')
             ])
        self.logger.info("Extended arguments: " + str(args))
        return args

    def set_driver_params(self):
        super(AmplifierFile, self).set_driver_params()
        self.set_tags()

    def store_driver_description(self, driver_output):
        super(AmplifierFile, self).store_driver_description(driver_output)
        self.set_param('sampling_rates', [int(self.get_param('sampling_rate'))])

    def set_tags(self):
        tags = read_tags_source.FileTagsSource(self.f_tags).get_tags()
        self.msg_mgr = tags_to_mxmsg.TagsToMxmsg(tags, self.config.get_param('tags_rules'))
        tss = ';'.join([repr(t['start_timestamp']) for t in tags])
        self._communicate("tags_start", timeout_s=0.1, timeout_error=False)
        self.logger.info("Start sending tss to driver...")
        self._communicate(tss, timeout_s=0.1, timeout_error=False)
        self.logger.info("Finished sending tss to driver!")
        self._communicate("tags_end", timeout_s=0.1, timeout_error=False)

    def got_trigger(self, ts):
        """Got trigger from the drivers.
        Let`s send next tag (or other message)
        with ts as its realtime timestamp"""
        # ...
        tp, msg = self.msg_mgr.next_message(ts)
        if tp is None:
            self.logger.warning("No tags left but got trigger. Should not happen!!!")
        else:
            self.logger.info("Send msg of type: " + str(tp))
            self.conn.send_message(
                message=msg,
                type=tp,
                flush=True)

    def do_sampling(self):
        self.logger.info("Stat waiting on drivers output...")
        while True:
            try:  # read tags from stdout
                v = self.driver_out_q.get_nowait()
                try:
                    ts = float(v)
                except ValueError:
                    if v.startswith('start OK'):
                        self.logger.info("Driver finished!!!")
                        break
                    else:
                        self.logger.warning("Got unrecognised message from driver: " + v)
                else:
                    self.logger.info("Got trigger with ts: " + repr(ts) + " / real ts: " + repr(time.time()))
                    self.got_trigger(ts)
            except queue.Empty:  # try reading other log from stderr
                try:
                    v = self.driver_err_q.get_nowait()
                    self.logger.info(v)
                except queue.Empty:
                    pass
                time.sleep(self.sleep_on_out)

        super(AmplifierFile, self).do_sampling()

if __name__ == "__main__":
    srv = AmplifierFile(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
