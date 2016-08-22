#!/usr/bin/env python3

from obci.control.launcher.obci_script import OBCIArgParser
import sys


def run():
    cmd_mgr = OBCIArgParser()
    cmd_mgr.setup_commands()
    if len(sys.argv) == 1:
        cmd_mgr.parser.print_help()
        sys.exit(1)
    args = cmd_mgr.parser.parse_args()
    args.func(args)
