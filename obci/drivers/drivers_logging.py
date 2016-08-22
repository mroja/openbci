#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

"""Module defines a single method get_logger that returns logger with
set logging level. Change loggin.INFO lines to change logging level."""
from obci.utils import openbci_logging


def get_logger(p_name, p_level='error'):
    """Return logger with p_name as name. And logging level p_level.
    p_level should be in (starting with the most talkactive):
    'debug', 'info', 'warning', 'error', 'critical'."""
    return openbci_logging.get_logger(p_name, p_level)
