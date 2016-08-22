#!/usr/bin/env python3

# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from obci.analysis.obci_signal_processing import read_manager

>>> import os, os.path, sys

>>> pth = os.path.abspath(read_manager.__file__)

>>> f = os.path.join(pth[:-len(os.path.basename(pth))], 'tests', 'data', 'data')

>>> mgr = read_manager.ReadManager(f+'.obci.info', f+'.obci.dat', f+'.obci.tags')

>>> mgr.get_samples(0, 1)[0,0]
-27075.0


>>> mgr.get_samples(0, 1)[1,0]
39641.0


>>> ch = mgr.get_samples()


>>> ch[0][0]
-27075.0

>>> ch[1][0]
39641.0

>>> [len(x) for x in ch]
[112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407,\
 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407,\
 112407, 112407, 112407, 112407, 112407, 112407, 112407]


>>> mgr.get_param(u'number_of_samples')
'2810175'

>>> mgr.get_param(u'sampling_frequency')
'128'

>>> mgr.get_param(u'number_of_channels')
'25'

>>> mgr.get_param('channels_names')
['Fp1', 'Fpz', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'M1', 'C7', 'C3',\
 'Cz', 'C4', 'T8', 'M2', 'P7', 'P3', 'Pz', 'P4', 'P8', 'O1', 'Oz', 'O2',\
 'NIC', 'OKO_GORA_DOL']


>>> mgr.get_param('im_not_there')
Traceback (most recent call last):
...
obci.analysis.obci_signal_processing.signal.signal_exceptions.NoParameter:\
 No parameter 'im_not_there' was found in info source!

>>> import numpy as np

>>> np.sum([np.abs(t['start_timestamp']-et)<0.0001 for t,et in zip(mgr.iter_tags(), [0.36085605621337891,\
 1.3654811382293701, 3.2938590049743652, 4.8368752002716064, 6.6318840980529785,\
8.2858760356903076, 9.8918850421905518, 11.599879026412964, 13.15486216545105, 14.747888088226318, 15.760866165161133,\
17.531879186630249, 19.168869018554688, 21.020870208740234, 22.716873168945312, 24.6128830909729, 26.412859201431274,\
28.320885181427002, 29.348877191543579, 30.735865116119385, 31.838881015777588, 33.505880117416382, 34.594882011413574,\
36.5418860912323, 37.700882196426392, 38.795868158340454, 40.185863971710205, 41.975889205932617, 43.608882188796997,\
44.695883989334106, 45.91289210319519, 47.635885000228882, 49.343885183334351, 50.655886173248291, 52.486284017562866,\
53.563876152038574, 55.53387713432312, 57.343875169754028, 59.317936182022095, 61.018882989883423, 62.311890125274658,\
63.758885145187378, 65.596870183944702, 67.496883153915405, 68.828874111175537, 70.646870136260986, 71.883864164352417,\
73.352570056915283, 75.352887153625488, 77.352883100509644, 78.996880054473877])])
51

>>> i = mgr.iter_tags()

>>> next(i)=={'channels': '', 'start_timestamp': 0.36085605621337891, 'desc': {u'value': u'1'}, 'name': u'trigger',\
'end_timestamp': 1.3654811382293701}
True

>>> next(i)=={'channels': '', 'start_timestamp': 1.3654811382293701, 'desc': {u'value': u'0'}, 'name': u'trigger',\
'end_timestamp': 3.2938590049743652}
True


"""


def run():
    import doctest
    import sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
