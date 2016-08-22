#!/usr/bin/env python3
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import struct
from .data_generic_write_proxy import DataGenericWriteProxy


class DataRawWriteProxy(DataGenericWriteProxy):

    def data_received(self, p_data):
        self._write_file(struct.pack(self._sample_struct_type, p_data))
        self._number_of_samples = self._number_of_samples + 1
