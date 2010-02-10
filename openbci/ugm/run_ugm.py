#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

"""Current script is supposed to be fired if you want to run 
ugm as a part of openbci (with multiplexer and all that stuff)."""
import socket, thread
import os

import variables_pb2

from ugm import ugm_engine
from ugm import ugm_config_manager
from ugm import ugm_server
from ugm import ugm_logging

LOGGER = ugm_logging.get_logger('run_ugm')

class TcpServer(object):
    """The class solves a problem with PyQt - it`s main window MUST be 
    created in the main thread. As a result I just can`t fire multiplexer
    and fire ugm_engine in a separate thread because it won`t work. I can`t
    fire ugm_engine and then fire multiplexer in a separate thread as 
    then multiplexer won`t work ... To solve this i fire ugm_engine in the 
    main thread, fire multiplexer in separate PROCESS and create TcpServer
    to convey data from multiplexer to ugm_engine."""
    def __init__(self, p_ugm_engine):
        """Init server and store ugm engine."""
        self._ugm_engine = p_ugm_engine
    def run(self):
        """Do forever:
        wait for data from ugm_server (it should be UgmUpdate() message
        type by now), parse data and send it to self._ugm_engine."""
        try:
            l_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Get config form ugm_server module
            l_soc.bind((ugm_server.TCP_IP, ugm_server.TCP_PORT))
            l_soc.listen(5)
            while True:
                # Wait for data from ugm_server
                l_conn = l_soc.accept()[0] # Don`t need address...
                l_full_data = ''
                while True:
                    l_data = l_conn.recv(ugm_server.BUFFER_SIZE)
                    if not l_data: 
                        break
                    l_full_data = ''.join([l_full_data, l_data])
                # d should represent UgmUpdate type...
                l_msg = variables_pb2.UgmUpdate()
                l_msg.ParseFromString(l_full_data)
                #LOGGER.debug(''.join(['TcpServer got: ',
                #                      str(l_msg.type),
                #                      ' / ',
                #                      l_msg.value]))
                # Not working properly while multithreading ...
                self._ugm_engine.update_from_message(
                    l_msg.type, l_msg.value)
                l_conn.close()
        except Exception, l_exc:
            LOGGER.error('An error occured in TcpServer: '+str(l_exc))
            raise(l_exc)
        finally:
            l_soc.close()

if __name__ == "__main__":
    # Create instance of ugm_engine with config manager (created from
    # default config file
    ENG = ugm_engine.UgmEngine(ugm_config_manager.UgmConfigManager())
    # Start TcpServer in a separate thread with ugm engine on slot
    thread.start_new_thread(TcpServer(ENG).run, ())
    # Start multiplexer in a separate process
    os.system("./openbci/ugm/ugm_server.py &")
    #TODO - works only when running from openbci directiory...
    # fire ugm engine in MAIN thread (current thread)
    ENG.run()

