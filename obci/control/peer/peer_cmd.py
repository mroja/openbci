#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse

from obci.control.common.config_helpers import LOCAL_PARAMS, EXT_PARAMS, CONFIG_SOURCES,\
    PEER_CONFIG_SECTIONS, LAUNCH_DEPENDENCIES, CS, LP, LD, EP

from obci.control.launcher.launcher_tools import expand_path

from . import peer_config_parser
from . import peer_config_serializer
from . import peer_config


class BasePeerCmdParser(object):

    def __init__(self, add_help=True):

        self.conf_parser = argparse.ArgumentParser(add_help=False)
        self.configure_argparser(self.conf_parser)

        self.parser = argparse.ArgumentParser(usage="%(prog)s peer_id base_config_file [options]", add_help=add_help,
                                              parents=[self.conf_parser])
        self.parser.add_argument('peer_id',
                                 help="Unique name for this instance of this peer")

    def configure_argparser(self, parser):

        parser.add_argument(LP, '--' + LOCAL_PARAMS,
                            nargs='+',
                            action=LocParamAction,
                            help="Local parameter override value: param_name, value.")  # ,
        # type=unicode)
        parser.add_argument(EP, '--' + EXT_PARAMS, nargs=2, action=ExtParamAction,
                            help="External parameter override value: param_name value .")

        parser.add_argument(CS, '--' + CONFIG_SOURCES, nargs=2, action=ConfigSourceAction,
                            help="Config source ID assignment: src_name peer_id")
        parser.add_argument(LD, '--' + LAUNCH_DEPENDENCIES, nargs=2, action=LaunchDepAction,
                            help="Launch dependency ID assignment: dep_name peer_id")

        parser.add_argument('-f', '--config_file', type=path_to_file, action='append',
                            help="Additional configuration files: [path_to_file].ini")
        # parser.add_argument('--wait-ready-signal', action='store_true',
        #                             help="Wait for init configuration message.")

    def parse_cmd(self, some_args=None):

        args = self.parser.parse_args(some_args)

        config_overrides = {}
        other_params = {}

        for attr, val in vars(args).items():
            if attr in PEER_CONFIG_SECTIONS:
                config_overrides[attr] = val if val is not None else {}
            else:
                other_params[attr] = val
        if other_params['config_file'] is None:
            other_params['config_file'] = []
        if other_params['config_file']:
            for f in other_params['config_file']:
                f = os.path.abspath(f)
        return config_overrides, other_params


class PeerCmd(BasePeerCmdParser):

    def __init__(self, add_help=True):
        super(PeerCmd, self).__init__(add_help)
        self.parser.add_argument('base_config_file', type=path_to_file,
                                 help="Base and mandatory configuration file for this peer.\n\
                            (there should be a your_module_name.ini in the same directory as your_module_name.")


class PeerParamAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        par, value = values[0], values[1]
        dic = getattr(namespace, self.dest)
        if dic is None:
            dic = {}
        dic[par] = value
        setattr(namespace, self.dest, dic)


class LocParamAction(PeerParamAction):

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) < 2:
            raise argparse.ArgumentTypeError("loc_param: Param name and value not specified!" + option_string)

        par = values[0]
        vals = []
        for v in values[1:]:
            vals.append(str(v))
        value = ' '.join(vals)
        dic = getattr(namespace, self.dest)
        if dic is None:
            dic = {}
        dic[par] = value
        setattr(namespace, self.dest, dic)


class ExtParamAction(PeerParamAction):
    pass


class ConfigSourceAction(PeerParamAction):
    pass


class LaunchDepAction(PeerParamAction):
    pass


def path_to_file(string):
    pth = expand_path(string)
    if not os.path.exists(pth):
        msg = "{} -- path not found!".format(pth)
        raise argparse.ArgumentTypeError(msg)
    return pth

# -----------------------------------------------------------------------------


def peer_overwrites_pack(args):
    ov_list = _peer_ovr_list(args)
    packed = [peer_args(ov) for ov in ov_list]
    return packed


def peer_overwrites_cmd(pack):
    args = ['--ovr']
    for [ovr, other] in pack:
        conf = peer_config.PeerConfig(peer_id=other['peer_id'])
        cfg_parser = peer_config_parser.parser('python')
        cfg_parser.parse(ovr, conf)
        args += ['--peer', other['peer_id']]
        ser = peer_config_serializer.PeerConfigSerializerCmd()
        ser.serialize(conf, args)
        if other['config_file']:
            for f in other['config_file']:
                args += ['-f', f]
    return args


def _peer_ovr_list(args):
    indices = [i for i, x in enumerate(args) if x == '-peer' or x == '--peer']
    if not indices:
        return []
    prev = indices[0]
    groupped = []
    for ind in indices[1:]:
        groupped.append(list(args[prev + 1:ind]))
        prev = ind
    groupped.append(list(args[prev + 1:]))
    return groupped


def peer_args(vals):
    print('cmd got', vals)
    pcmd = BasePeerCmdParser(add_help=False)
    ovr, other = pcmd.parse_cmd(vals)
    print(ovr, other)
    return [ovr, other]


if __name__ == "__main__":
    print(PeerCmd().parse_cmd())
