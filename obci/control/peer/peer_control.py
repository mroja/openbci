#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import numbers
import codecs
import logging

from . import peer_config
from . import peer_config_parser
from obci.control.peer.peer_cmd import PeerCmd
from .config_defaults import CONFIG_DEFAULTS

import obci.control.common.config_message as cmsg

from obci.configs import settings
from obci.utils.openbci_logging import log_crash

from obci.mx_legacy.multiplexer_constants import peers, types
from obci.mx_legacy.clients import connect_client

from functools import reduce

CONFIG_FILE_EXT = 'ini'
WAIT_READY_SIGNAL = "wait_ready_signal"
CONFIG_FILE = "config_file"
PEER_ID = "peer_id"
BASE_CONF = "base_config_file"

LOGGER = logging.getLogger("peer_control_default_logger")


class PeerControl(object):

    def __init__(self, peer=None, connection=None, param_validate_method=None,
                 param_change_method=None):
        self.core = peer_config.PeerConfig()
        self.peer = peer
        self.peer_validate_params = param_validate_method
        self.peer_params_changed = param_change_method

        self.peer_id = None
        self.base_config_path = None
        self.connection = connection
        self.query_conn = connect_client(type=peers.CONFIGURER,
                                         addresses=settings.MULTIPLEXER_ADDRESSES)

        self.cmd_overrides = {}
        self.file_list = []
        self.logger = LOGGER

        # parse command line
        self.process_command_line()
        self._load_provided_configs()

        if self.peer_validate_params:
            if self.connection:
                self.initialize_config(self.connection)
            else:
                self.initialize_config_locally()

    def initialize_config(self, connection):
        # self._load_provided_configs()

        self._request_ext_params(connection)

        # self.peer_validate_params(self.core.param_values)
        return self.config_ready()

    def initialize_config_locally(self):
        # self._load_provided_configs()
        # self.peer_validate_params(self.core.param_values)
        return self.config_ready()

    def _load_provided_configs(self):

        # parse default config file
        self._load_config_base()

        self._load_defaults(CONFIG_DEFAULTS)
        # parse external config file
        self._load_config_external()

        # parse other config files (names from command line)
        for filename in self.file_list:
            self._load_config_from_file(filename, CONFIG_FILE_EXT, update=True)

        # parse overrides (from command line)
        dictparser = peer_config_parser.parser('python')
        dictparser.parse(self.cmd_overrides, self.core, update=True)

    def _load_defaults(self, globals_):
        for param, val in globals_.items():
            self.core.add_local_param(param, val)

    def process_command_line(self):
        cmd_ovr, other_params = PeerCmd().parse_cmd()
        self.peer_id = self.core.peer_id = other_params[PEER_ID]
        self.base_config_path = other_params[BASE_CONF]
        if other_params[CONFIG_FILE] is not None:
            self.file_list = other_params[CONFIG_FILE]
        self.cmd_overrides = cmd_ovr

    def _load_config_external(self):
        """Parse the external configuration file, provided by peer"""

        if self.peer is None:
            raise NoPeerError
        if self.peer.external_config_file is not None:
            config_path = self.peer.external_config_file.rsplit('.', 1)[0]
            config_path = '.'.join([config_path, CONFIG_FILE_EXT])
            self._load_config_from_file(config_path, CONFIG_FILE_EXT)

    def _load_config_base(self):
        """Parse the base configuration file, named the same as peer's
        implementation file"""

        if self.peer is None:
            raise NoPeerError

        # print "Peer {0} base config path: {1}".format(self.peer_id, base_config_path)

        self._load_config_from_file(self.base_config_path, CONFIG_FILE_EXT)
        # print "Peer {0} base config: {1}".format(self.peer_id, self.core)

    def _load_config_from_file(self, p_path, p_type, update=False):
        with codecs.open(p_path, "r", "utf8") as f:
            parser = peer_config_parser.parser(p_type)
            parser.parse(f, self.core)

    def handle_config_message(self, mxmsg):

        if mxmsg.type in cmsg.MX_CFG_MESSAGES:
            message = cmsg.unpack_msg(mxmsg.type, mxmsg.message)

            msg, mtype = self._call_handler(mxmsg.type, message)
            if msg is None:
                self.peer.no_response()
            else:
                msg = cmsg.pack_msg(msg)
                self.peer.send_message(message=msg, type=mtype, to=int(mxmsg.from_), flush=True)

    def _call_handler(self, mtype, message):
        if mtype == types.PARAMS_CHANGED:
            return self._handle_params_changed(message)
        elif mtype == types.PEER_READY_SIGNAL:
            return self._handle_peer_ready_signal(message)
        elif mtype == types.SHUTDOWN_REQUEST:
            self.peer.shut_down()
            # return None, None
        else:
            return None, None

    def _handle_params_changed(self, p_msg):
        self.logger.info("PARAMS CHANGED - %s" % p_msg.sender)
        params = cmsg.params2dict(p_msg)
        param_owner = p_msg.sender

        old_values = {}
        updated = {}
        if param_owner in self.core.config_sources:
            src_params = self.core.params_for_source(param_owner)

            for par_name in [par for par in params if par in src_params]:
                old = self.core.get_param(par_name)
                new = params[par_name]
                if old != params[par_name]:
                    old_values[par_name] = old
                    updated[par_name] = new
                    self.core.set_param_from_source(p_msg.sender, par_name, new)
            if not self.peer_params_changed(updated):
                # restore...
                for par, val in old_values.items():
                    self.core.set_param_from_source(p_msg.sender, par, val)
        if param_owner == self.peer_id:
            local_params = self.core.local_params
            for par, val in params.items():
                if par not in local_params:
                    # protest?
                    continue
                if val != self.core.get_param(par):
                    old_values[par] = self.core.get_param(par)
                    updated[par] = val
                    self.core.update_local_param(par, val)

            if not self.peer_params_changed(updated):
                for par, val in old_values.items():
                    self.core.update_local_param(par, val)

        return None, None

    def config_ready(self):
        rd, details = self.core.config_ready()
        return rd and self.peer_id is not None, details

    def _handle_peer_ready_signal(self, p_msg):
        if not self.peer.ready_to_work and self.config_ready():
            self.peer.ready_to_work = True
            self.send_peer_ready(self.peer.conn)
            return None, None
        else:
            return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR

    @log_crash
    def get_param(self, p_name):
        return self.core.get_param(p_name)

    @log_crash
    def has_param(self, p_name):
        return self.core.has_param(p_name)

    @log_crash
    def set_param(self, p_name, p_value):
        result = self.core.update_local_param(p_name, p_value)
        # TODO let know other peers...
        if self.query_conn:
            msg = cmsg.fill_msg(types.UPDATE_PARAMS, sender=self.peer_id)
            params = {p_name: p_value}
            cmsg.dict2params(params, msg)
            self.__query(self.query_conn, msg,
                         types.UPDATE_PARAMS)
            # self.connection.send_message(message=msg, type=types.UPDATE_PARAMS)
            val_short = str(p_value)[:300] + '[...]'
            self.logger.info(' param update:: %s %s', p_name, val_short)
        else:
            self.logger.warning('param updated locally %s, %s, %s',
                                p_name, val_short, str(result))

        return result

    def param_values(self):
        return self.core.param_values

    def true_val(self, value):
        if isinstance(value, numbers.Number):
            return value > 0
        return str(value).lower() in ['1', 'true', 'yes', 't', 'y']

    def register_config(self, connection):
        if self.peer is None:
            raise NoPeerError()

        msg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender=self.peer_id)

        params = self.core.local_params
        cmsg.dict2params(params, msg)
        ext_params = self.core.ext_param_defs
        # register also external param definitions: param_name <---> (peer_id_of_config_source, param_name)
        for par in ext_params:
            ext_def = ext_params[par]
            symname = ext_def[0]
            ext_params[par] = (self.core.config_sources[symname], ext_def[1])

        cmsg.dict2params(ext_params, msg, field_name="ext_params")

        # connection.send_message(message=msg, type=types.REGISTER_PEER_CONFIG)
        reply = self.__query(connection, cmsg.pack_msg(msg),
                             types.REGISTER_PEER_CONFIG)
        # print 'AAAAAAAAAAAAAAAAAA', reply, "(rq:", types.REGISTER_PEER_CONFIG,\
        #                            "exp:", types.PEER_REGISTERED, ')'
        if reply is None:
            self.logger.error('config registration unsuccesful!!!! %s',
                              str(reply))
        elif not reply.type == types.PEER_REGISTERED:
            self.logger.error('config registration unsuccesful!!!! %s',
                              str(reply))

    def _request_ext_params(self, connection, retries=400):
        # TODO set timeout and retry count
        self.logger.info("requesting external parameters")
        if self.peer is None:
            raise NoPeerError

        def _unset_param_count():
            return reduce(lambda x, y: x + y,
                          [len(self.core.unset_params_for_source(src))
                           for src in self.core.used_config_sources()], 0)

        ready, details = self.core.config_ready()
        while not ready and retries:
            for src in self.core.used_config_sources():
                params = list(self.core.unset_params_for_source(src).keys())

                msg = cmsg.fill_msg(types.GET_CONFIG_PARAMS,
                                    sender=self.peer_id,
                                    param_names=params,
                                    receiver=self.core.config_sources[src])

                # print "requesting: {0}".format(msg)
                reply = self.__query(connection, cmsg.pack_msg(msg),
                                     types.GET_CONFIG_PARAMS)

                if reply is None:
                    # raise something?
                    continue

                if reply.type == types.CONFIG_ERROR:
                    self.logger.warning("peer {0} has not yet started".format(msg.receiver))

                elif reply.type == types.CONFIG_PARAMS:
                    reply_msg = cmsg.unpack_msg(reply.type, reply.message)
                    params = cmsg.params2dict(reply_msg)

                    for par, val in params.items():
                        self.core.set_param_from_source(reply_msg.sender, par, val)
                else:
                    self.logger.error("WTF? {0}".format(reply.message))

            # print '.',#"{0} external params still unset".format(_unset_param_count())
            time.sleep(0.4)
            ready, details = self.core.config_ready()
            retries -= 1

        if ready:
            self.logger.info("External parameters initialised %s",
                             str(self.core.config_ready()))

        return ready, details

    def send_peer_ready(self, connection):
        if self.peer is None:
            raise NoPeerError
        self.logger.info('sending ready signal.')
        mtype = types.PEER_READY
        msg = cmsg.fill_and_pack(mtype, peer_id=self.peer_id)

        self.__query(connection, msg, mtype)

        self._synchronize_ready(connection)

    def _synchronize_ready(self, connection):
        # TODO set timeout and retry count
        if self.peer is None:
            raise NoPeerError

        others = list(self.core.launch_deps.values())
        self.logger.info('waiting for other peers %s: ', str(others))
        msg = cmsg.fill_and_pack(types.PEERS_READY_QUERY, sender=self.peer_id,
                                 deps=others)

        ready = False
        while not ready:
            reply = self.__query(connection, msg, types.PEERS_READY_QUERY)
            # print 'got!', reply, cmsg.unpack_msg(reply.type, reply.message)
            if reply is None:
                # TODO sth bad happened, raise exception?

                continue
            if reply.type == types.READY_STATUS:
                rmsg = cmsg.unpack_msg(reply.type, reply.message)

                ready = rmsg.peers_ready
            if not ready:
                time.sleep(2)
        self.logger.info("Dependencies are ready, I can start working")

    def __query(self, conn, msg, msgtype):
        try:
            reply = conn.query(message=msg,
                               type=msgtype)
        except Exception:
            self.logger.exception("Query failed")
            reply = None
        return reply

# todo message verification


class PeerConfigControlError(Exception):

    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value is not None:
            return repr(self.value)
        else:
            return repr(self)


class ConfigNotReadyError(PeerConfigControlError):
    pass


class NoPeerError(PeerConfigControlError):
    pass


class PeerConfigControlWarning(Warning):
    pass


class UnsupportedMessageType(PeerConfigControlWarning):
    pass
