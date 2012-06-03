#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import random, time, pickle

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
from devices import appliance_helper
from acquisition import acquisition_helper
from gui.ugm import ugm_helper
from interfaces import interfaces_logging as logger
from analysis.buffers import auto_blink_buffer
from interfaces.hybrid.p300etr import p300_analysis_data_peer

from interfaces.hybrid.p300etr import csp_helper
from utils import streaming_debug

LOGGER = logger.get_logger("bci_p300_fda", "info")
DEBUG = True


#~ class BCIP300Fda(ConfiguredMultiplexerServer):
#~ 
    #~ def __init__(self, addresses):
        #~ #Create a helper object to get configuration from the system
        #~ super(BCIP300Fda, self).__init__(addresses=addresses,
                                          #~ type=peers.P300_ANALYSIS)
class P300Analysis(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(P300Analysis, self).__init__(addresses=addresses,
                                     type=peers.P300_ANALYSIS)
        self.ready()
        LOGGER = logger.get_logger("etr_analysis", "info")
        #get stats from file
        cfg = self._get_csp_config()
        #~ cfg['pVal'] = float(self.config.get_param('analysis_treshold'))
        
        montage_matrix = self._get_montage_matrix(cfg)
            
        #Create analysis object to analyse data 
        self.analysis = self._get_analysis(self.send_results, cfg, montage_matrix)

        #Initialise round buffer that will supply analysis with data
        #See auto_ring_buffer documentation
        sampling = int(self.config.get_param('sampling_rate'))
        channels_count = len(self.config.get_param('channel_names').split(';'))
        self.buffer = auto_blink_buffer.AutoBlinkBuffer(
            from_blink=0,
            samples_count=int(float(cfg['buffer'])),
            sampling=sampling,
            num_of_channels=channels_count,
            ret_func=self.analysis.analyse,
            ret_format=self.config.get_param('buffer_ret_format'),
            copy_on_ret=int(self.config.get_param('buffer_copy_on_ret'))
            )
        
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        if DEBUG:
            self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')),
                                               LOGGER,
                                               int(self.config.get_param('samples_per_packet')))
                                                   
        self._last_dec_time = time.time() + 1 #sleep 5 first seconds..
        ugm_helper.send_start_blinking(self.conn)
        #~ self.ready()
        LOGGER.info("BCIAnalysisServer init finished!")

    def send_results(self, results):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""
        LOGGER.info("Sending dec message: "+str(results))
        self._last_dec_time = time.time()
        #self.buffer.clear() dont do it in p300 - just ignore some blinks sometimes ...
        #self.buffer.clear_blinks()
        #ugm_helper.send_stop_blinking(self.conn)
        
        r = variables_pb2.Sample()
        r.timestamp = time.time()
        for i in range(len(results)):
            r.channels.append(float(results[i]))
        self.conn.send_message(message = r.SerializeToString(), type = types.P300_ANALYSIS_RESULTS, flush=True)

    def handle_message(self, mxmsg):
        #always buffer signal
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            #Supply buffer with sample data, the buffer will fire its
            #ret_func (that we defined as self.analysis.analyse) every 'every' samples
            #~ self.conn.send_message(message = str(l_msg), type = types.P300_ANALYSIS_RESULTS, flush=True)
            self.buffer.handle_sample_vect(l_msg)
            if DEBUG:
                self.debug.next_sample()

        if mxmsg.type == types.BLINK_MESSAGE:
            l_msg = variables_pb2.Blink()
            l_msg.ParseFromString(mxmsg.message)
            self.buffer.handle_blink(l_msg)
            
            #~ #process blinks only when hold_time passed
            #~ if self._last_dec_time > 0:
                #~ t = time.time() - self._last_dec_time
                #~ if t > self.hold_after_dec:
                    #~ self._last_dec_time = 0
                    #~ ugm_helper.send_start_blinking(self.conn)
                #~ else:
                    #~ self.no_response()
                    #~ return


            
        self.no_response()

    def _get_analysis(self, send_func, cfg, montage_matrix):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return p300_analysis_data_peer.BCIP300FdaAnalysis(
            send_func,
            cfg,
            montage_matrix,
            int(self.config.get_param('sampling_rate')))


    def _get_csp_config(self):
        return csp_helper.get_csp_config(
            self.config.get_param('config_file_path'),
            self.config.get_param('config_file_name'))

    def _get_montage_matrix(self, cfg):
        print "self.config.get_param('channel_names').split(';'): ", self.config.get_param('channel_names').split(';')
        print "cfg['use_channels'].split(';'): ", cfg['use_channels'].split(';')
        print "cfg['montage']: ",cfg['montage']
        print "cfg['montage_channels'].split(';'): ", cfg['montage_channels'].split(';')
        return csp_helper.get_montage_matrix(
            self.config.get_param('channel_names').split(';'),
            cfg['use_channels'].split(';'),
            cfg['montage'],
            cfg['montage_channels'].split(';'))
        

if __name__ == "__main__":
    P300Analysis(settings.MULTIPLEXER_ADDRESSES).loop()