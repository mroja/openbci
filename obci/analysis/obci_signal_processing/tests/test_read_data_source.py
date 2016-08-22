#!/usr/bin/env python3
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from obci.analysis.obci_signal_processing.signal.data_raw_write_proxy import DataRawWriteProxy

>>> import os.path, os

>>> # PREPARE SOME SAMPLE FILE *************************************************

>>> px = DataRawWriteProxy('./tescik.obci.dat')

>>> px.data_received(1.2)

>>> px.data_received(0.0023)

>>> px.data_received(-123.456)

>>> px.data_received(3.3)

>>> px.data_received(5.0)

>>> px.data_received(0.0)

>>> nic = px.finish_saving()

>>> f = './tescik.obci.dat'

>>> from obci.analysis.obci_signal_processing.signal import read_data_source as s

>>> # TEST MEMORY DATA SOURCE **************************************************

>>> import numpy

>>> import numpy as np

>>> py = s.MemoryDataSource(numpy.zeros((2,3)))

>>> py.set_sample(0, [1.0, 2.0])

>>> py.set_sample(1, [3.0, 4.0])

>>> py.set_sample(2, [5.0, 6.0])

>>> [i for i in py.iter_samples()]
[array([ 1.,  2.]), array([ 3.,  4.]), array([ 5.,  6.])]

>>> [i for i in py.iter_samples()]
[array([ 1.,  2.]), array([ 3.,  4.]), array([ 5.,  6.])]

>>> py.get_samples(0, 1)
array([[ 1.],
       [ 2.]])

>>> py.set_sample(3, [3.0, 4.0])
Traceback (most recent call last):
...
IndexError: index 3 is out of bounds for axis 1 with size 3

>>> py.set_sample(2, [1.0, 2.0, 3.0])
Traceback (most recent call last):
...
ValueError: cannot copy sequence with size 3 to array axis with dimension 2


>>> # TEST FILE DATA SOURCE ****************************************************

>>> py = s.FileDataSource(f, 2)

>>> py.get_samples(0, 0)
array([], shape=(2, 0), dtype=float64)

>>> np.abs(np.array([[  1.20000000e+00,  -1.23456000e+02],\
       [  2.30000000e-03,   3.30000000e+00]]) - py.get_samples(0, 2)) < 0.001
array([[ True,  True],
       [ True,  True]], dtype=bool)

>>> py.get_samples(0, 10)
Traceback (most recent call last):
...
obci.analysis.obci_signal_processing.signal.signal_exceptions.NoNextValue

>>> np.abs(np.array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],\
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]]) - py.get_samples(0, 3)) < 0.001
array([[ True,  True,  True],
       [ True,  True,  True]], dtype=bool)


>>> py.get_samples(1, 3)
Traceback (most recent call last):
...
obci.analysis.obci_signal_processing.signal.signal_exceptions.NoNextValue

>>> np.abs(np.array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],\
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]]) - py.get_samples()) < 0.001
array([[ True,  True,  True],
       [ True,  True,  True]], dtype=bool)

>>> py = s.FileDataSource(f, 2)

>>> from numpy import array

>>> np.abs(array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],\
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]]) - py.get_samples()) < 0.001
array([[ True,  True,  True],
       [ True,  True,  True]], dtype=bool)

>>> py = s.FileDataSource(f, 2)

>>> np.abs(array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],\
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]]) - py.get_samples()) < 0.001
array([[ True,  True,  True],
       [ True,  True,  True]], dtype=bool)

>>> np.abs(array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],\
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]]) - py.get_samples()) < 0.001
array([[ True,  True,  True],
       [ True,  True,  True]], dtype=bool)

>>> [max(abs(i-y))<0.0001 for i,y in zip(py.iter_samples(),\
 [array([ 1.2   ,  0.0023]), array([-123.456,    3.3  ]), array([ 5.,  0.])])]
[True, True, True]

>>> py = s.FileDataSource(f, 2)

>>> [max(abs(i-y))<0.0001 for i,y in zip(py.iter_samples(),\
[array([ 1.2   ,  0.0023]), array([-123.456,    3.3  ]), array([ 5.,  0.])])]
[True, True, True]

>>> [max(abs(i-y))<0.0001 for i,y in zip(py.iter_samples(),\
 [array([ 1.2   ,  0.0023]), array([-123.456,    3.3  ]), array([ 5.,  0.])])]
[True, True, True]

>>> os.remove(f)


"""


def run():
    import doctest
    import sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
