# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 200SAMPLE_SIZE-2009 Krzysztof Kulewski and Magdalena Michalska
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
#

import struct
import sys
import os.path
from openbci.data_storage import data_storage_exceptions
from openbci.data_storage import data_storage_logging as logger
LOGGER = logger.get_logger("data_file_proxy", 'info')
import time
SAMPLE_SIZE = 8 #float
BUF_SIZE = 4098*2
class DataFileWriteProxy(object):
    """
    A class representing data file. 
    It should be an abstraction for saving raw data into a file. 
    Decision whether save signal to one or few separate files should be made here 
    and should be transparent regarding below interface - the interface should remain untouched.
    Public interface:
    - finish_saving() - closes data file and return its path,
    - data_received(p_data_sample) - gets and saves next sample of signal
    """
    def __init__(self, p_file_name, p_dir_path, p_file_extension):
        """Open p_file_name file in p_dir_path directory."""
        self.buffer = [0.0]*BUF_SIZE
        self._number_of_samples = 0
        self._file_name = os.path.normpath(os.path.join(
                p_dir_path, p_file_name + p_file_extension))
        #TODO works in windows and linux on path with spaces?
        try:
            #TODO - co jesli plik istnieje?
            self._file = open(self._file_name, 'wr') #open file in a binary mode
        except IOError:
            LOGGER.error("Error! Can`t create a file!!!. parameters: " + str(p_file_name)+\
                        ", " + str(p_dir_path) + ", " + str(p_file_extension))
            sys.exit(1)
        self.t_wr = 0.0
        self.t_fl = 0.0
        self.t_full = 0.0

    def finish_saving(self):
        """Close the file, return a tuple - 
        file`s name and number of samples."""
        self._file.write(''.join(self.buffer[:(self._number_of_samples % BUF_SIZE)]))
        self._file.flush()
        self._file.close()
        return self._file_name, self._number_of_samples

    def data_received(self, p_data):
        """ Write p_data t self._file as raw float(C++ double). Here we assume, that
        p_data is of float type. 
        Type verification should be conducted earlier."""
        ind = self._number_of_samples % BUF_SIZE
        self.buffer[ind] = struct.pack("d", p_data)
        self._number_of_samples = self._number_of_samples + 1
        
        if (ind + 1) == BUF_SIZE:
            try:
                self._file.write(''.join(self.buffer))#struct.pack("d", p_data)) 
            except ValueError:
                LOGGER.error("Warning! Trying to write data to closed data file!")
                return
            except struct.error:
                LOGGER.error("Error while writhing to file. Bad sample format.")
                raise(data_storage_exceptions.BadSampleFormat())

        #store number of samples




class MxDataFileWriteProxy(object):
    """
    A class representing data file. 
    It should be an abstraction for saving raw data into a file. 
    Decision whether save signal to one or few separate files should be made here 
    and should be transparent regarding below interface - the interface should remain untouched.
    Public interface:
    - finish_saving() - closes data file and return its path,
    - data_received(p_data_sample) - gets and saves next sample of signal
    """
    def __init__(self, p_file_path):
        """Open p_file_name file in p_dir_path directory."""

        # A buffer for storing received data
        self.buffer = [0.0]*BUF_SIZE

        self._number_of_samples = 0

        self._file_path = p_file_path

        try:
            # Create a temporary file with .tmp extension
            # In finish_saving we read from that file and create another 
            # for efficency reasons
            self._file = open(self._file_path+'.tmp', 'wr') #open file in a binary mode
        except IOError:
            LOGGER.error("Error! Can`t create a file!!!. path: " +
                         str(self._file_path))
            sys.exit(1)

    def finish_saving(self, p_append_ts_index):
        """Save to temporary file all samples that are left in the buffer.
        As self._file contains protobuf values, now we need to once more read them,
        convert to number and save to another file in a standard format."""

        # Save to temp file remaining values
        self._file.write(''.join(self.buffer[:(self._number_of_samples % BUF_SIZE)]))
        self._file.flush()
        self._file.close()
        
        final_file = open(self._file_path, 'w')
        
        import variables_pb2

        # Open once more temporary file with protobuf data
        temp_file = open(self._file_path+'.tmp', 'r')
        msg = ' '
        while len(msg) > 0:
            msg = temp_file.read(self._data_len)
            l_vec = variables_pb2.SampleVector()
            l_vec.ParseFromString(msg)
            for i, i_sample in enumerate(l_vec.samples):
                ts = i_sample.timestamp

                if i == p_append_ts_index:
                    try:
                        final_file.write(struct.pack("d", ts))
                    except struct.error:
                        LOGGER.error("Error while writhing to file. Bad sample format.")
                        raise(data_storage_exceptions.BadSampleFormat())
                    
                try:
                    final_file.write(struct.pack("d", i_sample.value))
                except struct.error:
                    LOGGER.error("Error while writhing to file. Bad sample format.")
                    raise(data_storage_exceptions.BadSampleFormat())
            # p_append_ts_index might be the last channel
            if p_append_ts_index == i + 1:
                    try:
                        final_file.write(struct.pack("d", ts))
                    except struct.error:
                        LOGGER.error("Error while writhing to file. Bad sample format.")
                        raise(data_storage_exceptions.BadSampleFormat())
                


        final_file.flush()
        final_file.close()
        
        # Close and remove temporary file
        temp_file.close()
        os.remove(self._file_path+'.tmp')


        return self._file_path, self._number_of_samples
    def set_data_len(self, ln):
        """Set length of one unit of protobuf data
        stored in temporary file. It`ll be useful
        in finish_saving() while extracting data from the file."""

        self._data_len = ln

    def data_received(self, p_data):
        """ p_data must be protobuf SampleVector message, but serialized to string.
        Data is stored in temp buffer, once a while the buffer is flushed to a file."""

        ind = self._number_of_samples % BUF_SIZE
        self.buffer[ind] = p_data
        self._number_of_samples = self._number_of_samples + 1

        if (ind + 1) == BUF_SIZE:
            # The buffer is full
            try:
                self._file.write(''.join(self.buffer))
            except ValueError:
                LOGGER.error("Warning! Trying to write data to closed data file!")
                return





class AsciFileWriteProxy(object):
    def __init__(self, p_file_name, p_dir_path, p_file_extension):
        """Open p_file_name file in p_dir_path directory."""
        self._file_name = os.path.normpath(os.path.join(
                p_dir_path, p_file_name + p_file_extension))
        try:
            self._file = open(self._file_name, 'w') #open file in a binary mode
        except IOError:
            print "Error! Can`t create a file!!!."
            sys.exit(1)

    def finish_saving(self):
        """Close the file, return a tuple - 
        file`s name and number of samples."""
        self._file.close()
        return self._file_name

    def data_received(self, p_data):
        """ Write p_data t self._file as raw int. Here we assume, that
        p_data is of float type. 
        Type verification should be conducted earlier."""
        try:
            self._file.write(repr(p_data)+'\n')
        except ValueError:
            print("Warning! Trying to write data to closed data file!")
            return
        
        self._file.flush()







class DataFileReadProxy(object):
    def __init__(self, p_file_path):
        self._file_path = p_file_path
        
    def start_reading(self):
        try:
            self._data_file = open(self._file_path, 'rb')
        except IOError, e:
            LOGGER.error("An error occured while opening the data file!")
            raise(e)
    def get_next_value(self):
        """Return next value from data file (as python float). 
        Close data file and raise NoNextValue exception if eof."""
        l_raw_data = self._data_file.read(SAMPLE_SIZE)
        try:
            #TODO - by now it is assumed that error means eof.. 
            #What if it is not eof but eg. 4-chars 
            #string from the end of a broken file?
            return struct.unpack('d', l_raw_data)[0]
        except struct.error:
            self._data_file.close()
            raise(data_storage_exceptions.NoNextValue())

    def goto_value(self, p_value_no):
        """Set the engine, so that nex 'get_next_value' call will return
        value number p_value_no+1. 
        Eg. if p_value_no == 0, calling get_next_value will return first value.
        if p_value_no == 11, calling get_next_value will return 12-th value."""
        LOGGER.debug("DOING SEEK TO: "+str(p_value_no))
        self._data_file.seek(p_value_no * SAMPLE_SIZE)
        LOGGER.debug("DATA FILE SEEK DONE. CURRENT POSITION/8 = "+str(self._data_file.tell()/8))

