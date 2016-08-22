#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

from obci.control.launcher.obci_script_utils import (server_process_running,
                                                     client_server_prep,
                                                     disp)

from obci.control.launcher import obci_server

from obci.control.peer.peer_cmd import PeerCmd
import obci.control.peer.peer_cmd as peer_cmd


def cmd_srv(args):
    client_server_prep(args)


def cmd_srv_kill(args):
    running = server_process_running(expected_dead=True)
    if not running:
        disp.view("Server was not running...")
        return

    client = client_server_prep()
    if not client:
        print("srv_kill unsuccessful (client creation error)")
        sys.exit(1)
    client.srv_kill()

    if server_process_running(expected_dead=True):
        disp.view('obci server kill signal unsuccesful, try killing the process')
    else:
        disp.view("Server process terminated.")


def cmd_launch(args):
    launch_f = os.path.abspath(args.launch_file)
    overwrites = args.ovr
    if overwrites:
        pack = peer_cmd.peer_overwrites_pack(overwrites)
        print(pack)
    else:
        pack = None

    client = client_server_prep(start_srv=False)
    if not client:
        sys.exit(1)

    response = client.launch(launch_f, args.sandbox_dir, args.name, pack)
    disp.view(response)


def cmd_morph(args):
    launch_f = os.path.abspath(args.launch_file)
    overwrites = args.ovr
    if overwrites:
        pack = peer_cmd.peer_overwrites_pack(overwrites)
        print(pack)
    else:
        pack = None

    client = client_server_prep()
    if not client:
        sys.exit(1)
    print(args.leave_on)
    response = client.morph(args.experiment, launch_f, args.name, pack, args.leave_on)
    disp.view(response)


def cmd_new(args):
    if args.launch_file:
        launch_f = os.path.abspath(args.launch_file)
    else:
        launch_f = ''
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.send_create_experiment(launch_f, args.sandbox_dir, args.name)
    disp.view(response)


def cmd_start(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.start_chosen_experiment(args.experiment)
    disp.view(response)


def cmd_join(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.join_experiment(args.id, args.peer_id, args.peer_path)
    if response.type == 'rq_ok':
        pass
    disp.view(response)


def cmd_kill(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.kill_exp(args.id)
    disp.view(response)


def cmd_killall(args):
    pass


def cmd_add(args):
    pass


def cmd_save(args):
    pass


def cmd_log(args):
    pass


def cmd_config(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    ovr = dict(local_params=args.local_params,
               external_params=args.external_params,
               launch_dependencies=args.launch_dependencies,
               config_sources=args.config_sources)

    response = client.configure_peer(args.experiment, args.peer_id, ovr,
                                     args.config_file)
    disp.view(response)


def cmd_info(args):
    client = client_server_prep(start_srv=False)
    if not client:
        sys.exit(1)
    if not args.experiment:
        response = client.send_list_experiments()
    else:
        response = client.get_experiment_details(args.experiment, args.peer_id)
    if response is None:
        response = "whyyyy"
    disp.view(response)


def cmd_tail(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    if not args.e:
        response = client.send_list_experiments()
    elif not args.p:
        response = client.get_experiment_details(args.e, args.p)
    else:
        response = client.get_tail(args.e, args.p, args.l)
    if response is None:
        response = "whyyyy"
    disp.view(response)

#


def setup_srv(parser_srv):
    parser_srv.set_defaults(func=cmd_srv)


def setup_srv_kill(parser_srv_kill):
    parser_srv_kill.set_defaults(func=cmd_srv_kill)


def setup_launch(parser_launch):
    parser_launch.add_argument('launch_file', type=path_to_file,
                               help="OpenBCI launch configuration (experiment configuration).")
    parser_launch.add_argument('--sandbox_dir', type=path_to_file,
                               help="Directory for log file and various temp files storeage.")
    parser_launch.add_argument('--name',
                               help="A name for experiment")
    parser_launch.add_argument('--ovr', nargs=argparse.REMAINDER)  # , type=peer_args)
    parser_launch.set_defaults(func=cmd_launch)


def setup_morph(parser_morph):
    parser_morph.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_morph.add_argument('launch_file', type=path_to_file,
                              help="OpenBCI launch configuration (experiment configuration).")
    parser_morph.add_argument('--name',
                              help="A name for experiment")
    parser_morph.add_argument('--leave_on', nargs='*',  # action='append',
                              help="A name for experiment")
    parser_morph.add_argument('--ovr', nargs=argparse.REMAINDER)
    parser_morph.set_defaults(func=cmd_morph)


def setup_kill(parser_kill):
    parser_kill.add_argument('id', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_kill.add_argument('--brutal', help='Just kill the specified experiment manager, \
do not send a "kill" message')
    parser_kill.set_defaults(func=cmd_kill)


def setup_info(parser_info):
    parser_info.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)', nargs='?', default='')
#     parser_info.add_argument('-e', help='Something that identifies experiment: \
# a few first letters of its UUID or of its name \
# (usually derived form launch file name)')
    # parser_info.add_argument('-p', help='Peer ID in the specified experiment.')
    parser_info.add_argument('peer_id', help='Peer ID in the specified experiment.',
                             nargs='?', default='')
    parser_info.set_defaults(func=cmd_info)


# temporarily unsupported commands ########################

def setup_add(parser_add):
    pass


def setup_new(parser_new):
    parser_new.add_argument('--launch_file', type=path_to_file,
                            help="OpenBCI launch configuration (experiment configuration).")
    parser_new.add_argument('--sandbox_dir', type=path_to_file,
                            help="Directory for log file and various temp files storeage.")
    parser_new.add_argument('--name',
                            help="A name for experiment")
    parser_new.set_defaults(func=cmd_new)


def setup_start(parser_start):
    parser_start.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_start.set_defaults(func=cmd_start)


def setup_killall(parser_killall):
    pass


def setup_join(parser_join):
    parser_join.add_argument('id', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_join.add_argument('peer_id',
                             help="Unique name for this peer")
    parser_join.add_argument('peer_path', type=path_to_file,
                             help="Path to an executable file.")
    parser_join.set_defaults(func=cmd_join)


def setup_save(parser_save):
    pass


def setup_config(parser_config):
    parser_config.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_config.add_argument('peer_id', help='Peer ID in the specified experiment.')
    parser_config.set_defaults(func=cmd_config)


def setup_tail(parser_tail):
    parser_tail.add_argument('-e', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_tail.add_argument('-p', help='Peer ID in the specified experiment.')
    parser_tail.add_argument('-l', help='Number of lines to get')
    parser_tail.set_defaults(func=cmd_tail)

# end of unsupported commands ###########################


class OBCIArgParser(object):
    defined_commands = {
        "launch": dict(help="Launch an OpenBCI system with configuration \
specified in a launch file or in a newly created Experiment",
                       setup_func=setup_launch),
        "srv": dict(parser_parents=[obci_server.server_arg_parser(add_help=False)],
                    help="Start OBCIServer",
                    setup_func=setup_srv),
        "srv_kill": dict(parser_parents=[obci_server.server_arg_parser(add_help=False)],
                         help="Kill OBCIServer",
                         setup_func=setup_srv_kill),
        "morph": dict(help='Transform chosen running scenario into another.\
Optionally leave some peers running instead of restarting them',
                      setup_func=setup_morph),
        "info": dict(help="Get information about controlled OpenBCI experiments\
                        and peers",
                     setup_func=setup_info),
        "kill": dict(help="Kill an OpenBCI experiment",
                     setup_func=setup_kill)
    }

    def __init__(self,
                 description="Launch and manage OBCI experiments,their state and configuration",
                 epilog="(c) 2011-2016, Warsaw University",
                 prog='obci'):
        self.parser = argparse.ArgumentParser(description=description,
                                              epilog=epilog,
                                              prog=prog)
        self.subparsers = self.parser.add_subparsers(
            title='available commands',
            description='(use %(prog)s *command* -h for help on a specific command)',
            dest='command_name')
        self.conf_parser = PeerCmd().conf_parser
        self._commands = {}

    def _create_command_parser(self, name, help_text, parser_parents=None):
        parents = parser_parents if parser_parents is not None else []
        new_parser = self.subparsers.add_parser(name, help=help_text, parents=parents)
        self._commands[name] = new_parser
        return new_parser

    def _setup_command_parser(self, parser, setup_func):
        setup_func(parser)

    def add_command(self, name, help, setup_func, parser_parents=None):
        parser = self._create_command_parser(name, help, parser_parents)
        self._setup_command_parser(parser, setup_func)

    def setup_commands(self, cmd_defs={}):
        for defs in [self.defined_commands, cmd_defs]:
            self._setup_commands(defs)

    def _setup_commands(self, command_defs):
        for name in sorted(command_defs):
            self.add_command(name, **command_defs[name])


#
#


def path_to_file(string):
    if not os.path.exists(string):
        raise argparse.ArgumentTypeError("{0} -- path not found!".format(string))
    return string
