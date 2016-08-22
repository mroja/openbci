#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json

from obci.utils import openbci_logging as logger


DISCOVERY_MODULE_NAMES = [
    'amplifier_virtual_discovery',
    'amplifier_tmsi_bt_discovery',
    'amplifier_tmsi_usb_discovery',
]
BASE_MODULE = 'obci.drivers.eeg.driver_discovery'

LOADED_MODULE_NAMES = []

discovery_modules = []

LOGGER = logger.get_logger("DriverDiscovery", "info")

for mod_name in DISCOVERY_MODULE_NAMES:
    name = BASE_MODULE + '.' + mod_name
    try:
        __import__(name)

    except ImportError:
        LOGGER.error("could not import discovery module %s" % name)
        continue
    discovery_modules.append(sys.modules[name])
    LOADED_MODULE_NAMES.append(mod_name)


def find_drivers():
    return _find_amps(discovery_modules)


def _filter_modules(pattern):
    return [sys.modules[BASE_MODULE + '.' + mod] for mod in LOADED_MODULE_NAMES if pattern in mod]


def _find_amps(module_list):
    descriptions = []
    for mod in module_list:
        try:
            descriptions += mod.driver_descriptions()
        except Exception as e:
            LOGGER.warning("Discovery failed: " + str(mod))
    return descriptions


def find_usb_amps():
    modules = _filter_modules('usb')
    return _find_amps(modules)


def find_bluetooth_amps():
    modules = _filter_modules('bt')
    return _find_amps(modules)


def find_virtual_amps():
    modules = _filter_modules('virtual')
    return _find_amps(modules)

if __name__ == '__main__':
    drivers = find_drivers()
    print(json.dumps(drivers, indent=4))
