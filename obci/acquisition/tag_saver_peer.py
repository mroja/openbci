#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from obci.mx_legacy.multiplexer_constants import peers, types

import sys
import os.path
import time
from obci.configs import settings, variables_pb2
from obci.analysis.obci_signal_processing.tags import tags_file_writer as tags_writer
from obci.analysis.obci_signal_processing.tags import tag_utils

from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.utils.openbci_logging import log_crash

TAG_FILE_EXTENSION = ".obci.tag"


class TagSaver(ConfiguredMultiplexerServer):

    @log_crash
    def __init__(self, addresses, peer_type=peers.TAG_SAVER):
        """Init slots."""
        super(TagSaver, self).__init__(addresses=addresses,
                                       type=peer_type)
        # Get file path data
        l_f_name = self.config.get_param("save_file_name")
        l_f_dir = self.config.get_param("save_file_path")
        self._file_path = os.path.expanduser(os.path.normpath(os.path.join(
            l_f_dir, l_f_name + TAG_FILE_EXTENSION)))

        self._tags_proxy = tags_writer.TagsFileWriter(self._file_path)
        self.ready()
        self._session_is_active = True

    def handle_message(self, mxmsg):
        """Handle messages:
        * Tag message - raw data from mx (TAG)
        If session is active convey data to save_manager.
        * signal_saver_control_message - a message from signal saver
        is a signal to finishing saving tags.
        depending on data received."""
        if mxmsg.type == types.TAG and \
                self._session_is_active:
            str_tag = variables_pb2.Tag()
            str_tag.ParseFromString(mxmsg.message)
            tag_desc = dict()
            for i_var in str_tag.desc.variables:
                tag_desc[i_var.key] = i_var.value
            l_tag = tag_utils.pack_tag_to_dict(str_tag.start_timestamp, str_tag.end_timestamp,
                                               str_tag.name, tag_desc, str_tag.channels)

            self.logger.info(''.join(['Tag saver got tag: ',
                                      'start_timestamp:',
                                      repr(l_tag['start_timestamp']),
                                      ', end_timestamp: ',
                                      repr(l_tag['end_timestamp']),
                                      ', name: ',
                                      l_tag['name'],
                                      '. <Change debug level to see desc.>']))

            self.logger.debug("Signal saver got tag: " + str(l_tag))
            self._tag_received(l_tag)
        elif mxmsg.type == types.ACQUISITION_CONTROL_MESSAGE:
            ctr = mxmsg.message.decode()
            if ctr == 'finish':
                if not self._session_is_active:
                    self.logger.error("Attempting to finish saving tags while session is not active.!")
                    return
                self._session_is_active = False
                self.logger.info("Got finish saving message. Waiting for saver_finished message...")
            else:
                self.logger.warning("Tag saver got unknown control message " + ctr + "!")

        elif mxmsg.type == types.__dict__[self.config.get_param("finished_signal_type")]:
            if self._session_is_active:
                self.logger.warning(
                    "Got saver_finished before getting saver control message... \
                    This shouldn`t happen, but continue anyway...")
                self._session_is_active = False

            l_vec = variables_pb2.VariableVector()
            l_vec.ParseFromString(mxmsg.message)
            for i_var in l_vec.variables:
                # Assume that first_sample_timestamp key is
                # in a dictinary got from signal saver
                if i_var.key == 'first_sample_timestamp':
                    self._finish_saving(float(i_var.value))
                    time.sleep(3)
                    sys.exit(0)
            self.logger.error("Got saver finished message without first_sample_timestamp. Do noting ...")
        self.no_response()

    def _finish_saving(self, p_first_sample_ts):
        """Save all tags to xml file, but first update their
        .position field so that it is relative to timestamp
        of a first sample stored by signal saver (p_first_sample_ts)."""

        # Save tags
        self.logger.info("Finish saving with first sample ts: " + str(p_first_sample_ts))
        l_file_path = self._tags_proxy.finish_saving(p_first_sample_ts)

        l_vec = variables_pb2.VariableVector()
        l_var = l_vec.variables.add()
        l_var.key = 'file_path'
        l_var.value = self._file_path

        self.conn.send_message(
            message=l_vec.SerializeToString(),
            type=types.__dict__[self.config.get_param("finished_tag_type")],
            flush=True)

        self.logger.info("Tags file saved to: " + l_file_path)
        return l_file_path

    def _tag_received(self, p_tag_dict):
        """Convey tag to tags_proxy."""
        self._tags_proxy.tag_received(p_tag_dict)

if __name__ == "__main__":
    TagSaver(settings.MULTIPLEXER_ADDRESSES).loop()
