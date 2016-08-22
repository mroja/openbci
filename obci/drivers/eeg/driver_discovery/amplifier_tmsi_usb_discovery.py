#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os

from obci.control.launcher.launcher_tools import obci_root, READY_TO_LAUNCH
from obci.control.peer.peer_config import PeerConfig
from obci.drivers.eeg.driver_comm import DriverComm

_DESC_BASE_PATH = os.path.join(obci_root(), 'drivers/eeg/driver_discovery')

_TYPES = ['Porti7']

_USB_DESCS = {'Porti7': 'amplifier_porti7_usb.json',
              'SynFi': 'amplifier_tmsi_synfi.json'}
_AMP_PEER = 'drivers/eeg/cpp_amplifiers/amplifier_tmsi.py'
_AMP_EXECUTABLE = 'tmsi_amplifier'
_SCENARIO = 'scenarios/amplifier/tmsi_amp_signal.ini'


def _find_usb_amps():
    dev_path = os.path.realpath('/dev')
    amps = [dev for dev in os.listdir(dev_path) if
            dev.startswith('fusbi')]

    synfi_amps = [dev for dev in os.listdir(dev_path) if
                  dev.startswith('synfi')]
    amps = [os.path.join(dev_path, dev) for dev in amps]
    synfi_amps = [os.path.join(dev_path, dev) for dev in synfi_amps]
    amps = [(dev, '', 'Porti7') for dev in amps if os.readlink(dev).startswith('tmsi')]
    synfi_amps = [(dev, '', 'SynFi') for dev in synfi_amps if os.readlink(dev).startswith('tmsi')]
    amps += synfi_amps

    print("Found USB devices: ", amps)
    return amps


def get_description_from_driver(device_path):
    conf = PeerConfig('amplifier')
    conf.add_local_param('driver_executable', _AMP_EXECUTABLE)
    conf.add_local_param('samples_per_packet', '4')
    conf.add_local_param('bluetooth_device', '')
    conf.add_local_param('usb_device', device_path)

    driv = DriverComm(conf, catch_signals=False)
    descr = driv.get_driver_description()
    try:
        dic = json.loads(descr)
    except ValueError as e:
        print("AMPLIFIER ", device_path, "IS PROBABLY BUSY.", end=' ')
        print("Invalid channel description: ", descr)
        dic = None

    driv.terminate_driver()
    return dic


def driver_descriptions():
    descriptions = []
    usb = _find_usb_amps()

    for amp in usb:

        desc = {
            'experiment_info': {
                "launch_file_path": _SCENARIO,
                'experiment_status': {
                    'status_name': READY_TO_LAUNCH
                }
            },
            'amplifier_peer_info': {
                'driver_executable': _AMP_EXECUTABLE,
                'path': _AMP_PEER},

            'amplifier_params': {

                'additional_params': {'usb_device': '',
                                      'bluetooth_device': ''},
                'active_channels': '',
                'channel_names': '',
                'sampling_rate': ''},
        }

        desc['amplifier_params']['additional_params']['usb_device'] = amp[0]
        # with open(os.path.join(_DESC_BASE_PATH, _USB_DESCS[amp[2]])) as f:
        #     desc['amplifier_params']['channels_info'] = json.load(f)
        chan_inf = get_description_from_driver(amp[0])
        if chan_inf is None:
            # amplifier busy or an error occurred
            continue
        else:
            desc['amplifier_params']['channels_info'] = chan_inf
            descriptions.append(desc)

    return descriptions
