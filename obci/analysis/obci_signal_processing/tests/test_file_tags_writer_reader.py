#!/usr/bin/env python3

# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from obci.analysis.obci_signal_processing.tags import tags_file_writer as p

>>> from obci.analysis.obci_signal_processing.tags import tags_file_reader as t

>>> px = p.TagsFileWriter('./tescik.obci.tags')

>>> px.tag_received({'start_timestamp':1001.0, 'end_timestamp':1002.0, 'name': 'nic', 'channels':'A B C',\
                    'desc': {'x':123, 'y':456, 'z': 789}})

>>> px.tag_received({'start_timestamp':1003.0, 'end_timestamp':1004.0, 'name': 'nic2', 'channels':'A B C',\
                    'desc': {'x':1234, 'y':4567, 'z': 789}})

>>> px.tag_received({'start_timestamp':1005.0, 'end_timestamp':1006.0, 'name': 'nic3', 'channels':'A B C',\
                    'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> px.finish_saving(1000.0)
'./tescik.obci.tags'

>>> py = t.TagsFileReader('tescik.obci.tags')

>>> g = py.get_tags()[0]

>>> print(g['start_timestamp'])
1.0

>>> print(g['end_timestamp'])
2.0

>>> print(g['name'])
nic

>>> print(g['desc']['y'])
456

>>> print([int(t['start_timestamp']) for t in py.get_tags()])
[1, 3, 5]


>>> #REORDER AND TEST ORDERING AGAIN ....

>>> px = p.TagsFileWriter('./tescik.obci.tags')

>>> px.tag_received({'start_timestamp':1003.0, 'end_timestamp':1004.0, 'name': 'nic2', 'channels':'A B C',\
                     'desc': {'x':1234, 'y':4567, 'z': 789}})

>>> px.tag_received({'start_timestamp':1005.0, 'end_timestamp':1006.0, 'name': 'nic3', 'channels':'A B C',\
                    'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> px.tag_received({'start_timestamp':1001.0, 'end_timestamp':1002.0, 'name': 'nic', 'channels':'A B C',\
                    'desc': {'x':123, 'y':456, 'z': 789}})

>>> print([int(t['start_timestamp']) for t in py.get_tags()])
[1, 3, 5]

>>> import os

>>> import glob

>>> for fl in glob.glob('tescik*'): os.remove(fl)

"""


def run():
    import doctest
    import sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
