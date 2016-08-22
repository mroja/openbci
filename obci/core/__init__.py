"""
This module contains core modules for OpenBCI framework such as Broker, Peer and Message.
"""

import os

OBCI_DEBUG = True if 'OBCI_DEBUG' in os.environ else False
"""bool: Set to True if `OBCI_DEBUG` environment variable is defined.

If enabled sets root logger level to `DEBUG` and enables all warnings
generated using `warnings` module.
"""

# Uncomment to force debug.
# OBCI_DEBUG = True  # noqa

if OBCI_DEBUG:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import warnings
    warnings.simplefilter('default')

__all__ = ['OBCI_DEBUG']
