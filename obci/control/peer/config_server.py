#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import time
import json
import configparser
import os


from obci.mx_legacy.multiplexer_constants import peers, types
from obci.mx_legacy.clients import BaseMultiplexerServer
from obci.control.peer.peer_cmd import PeerCmd
from obci.configs import settings


import obci.control.common.config_message as cmsg
from obci.control.common.obci_control_settings import DEFAULT_SANDBOX_DIR
from obci.control.launcher.launcher_messages import message_templates
from obci.control.common.message import OBCIMessageTool, send_msg

from obci.utils.openbci_logging import get_logger, log_crash


class ConfigServer(BaseMultiplexerServer):

    @log_crash
    def __init__(self, addresses):
        super(ConfigServer, self).__init__(addresses=addresses, type=peers.CONFIG_SERVER)
        self._configs = {}
        self._ext_configs = {}
        self._ready_peers = []
        self.__to_all = False
        self.mtool = OBCIMessageTool(message_templates)
        self.launcher_sock = None
        params, other_params = PeerCmd().parse_cmd()

        self.addr = params['local_params'].get('launcher_socket_addr', '')

        self.exp_uuid = params['local_params'].get('experiment_uuid', '')
        self.log_dir = params['local_params'].get('log_dir', None)
        self.logger = get_logger('config_server', log_dir=self.log_dir,
                                 conn=self.conn,
                                 file_level=params['local_params'].get('file_log_level', None),
                                 mx_level=params['local_params'].get('mx_log_level', None),
                                 stream_level=params['local_params'].get('console_log_level', None))
        self._old_configs = self._stored_config()
        self._restore_peers = params['local_params'].get('restore_peers', '').split()

        for peer in self._restore_peers:
            if peer in self._old_configs["local"]:
                self._configs[peer] = dict(self._old_configs["local"][peer])
                self._ready_peers.append(peer)
            if peer in self._old_configs["ext"]:
                self._ext_configs[peer] = dict(self._old_configs["ext"][peer])

        if self.addr != '':
            self.ctx = zmq.Context()
            self.launcher_sock = self.ctx.socket(zmq.PUSH)
            try:
                self.launcher_sock.connect(self.addr)

            except Exception as e:
                self.logger.error("failed to connect to address " +
                                  self.addr + " !!!")
                self.launcher_sock = None
            else:
                self.logger.info("OK: connected to " + self.addr)

                send_msg(self.launcher_sock, self.mtool.fill_msg("config_server_ready"))
        self.logger.info("connections count ::::::::: %s", self.conn.connections_count())

    def _config_path(self):
        base_config_path = "config_server.ini"
        return os.path.abspath(os.path.join(DEFAULT_SANDBOX_DIR, base_config_path))

    def _stored_config(self):
        parser = configparser.RawConfigParser()
        stored = None
        storedconf = self._config_path()
        if not os.path.exists(storedconf):
            self.logger.info("No config stored %s", str(storedconf))
        else:
            with open(storedconf, 'r') as f:
                self.logger.info("found stored config %s", str(storedconf))
                parser.readfp(f)
        if not parser.has_option('local_params', 'stored_config'):
            stored = ''
        else:
            stored = parser.get('local_params', 'stored_config')
        if stored == '':
            stored = '{}'
        return json.loads(stored)

    def _save_config(self):
        base_config_path = self._config_path()
        parser = configparser.RawConfigParser()
        # print "CONFIG_SERVER save path", base_config_path
        if os.path.exists(base_config_path):
            with open(base_config_path, 'r') as f:
                parser.readfp(f)
        if not parser.has_section('local_params'):
            parser.add_section('local_params')

        parser.set('local_params', 'stored_config', json.dumps({"local": self._configs, "ext": self._ext_configs}))
        parser.set('local_params', 'launcher_socket_addr', '')
        parser.set('local_params', 'experiment_uuid', '')
        parser.set('local_params', 'restore_peers', '')

        with open(base_config_path, 'w') as f:
            parser.write(f)
        try:
            os.chmod(base_config_path, 0o777)
        except OSError as e:
            self.logger.error("tried to change permissions to" +
                              base_config_path + "to 777 but" + str(e))
        else:
            self.logger.info("changed permissions to " + base_config_path + " to 777")

    @log_crash
    def handle_message(self, mxmsg):

        message = cmsg.unpack_msg(mxmsg.type, mxmsg.message)

        msg, mtype, launcher_msg = self._call_handler(mxmsg.type, message)
        if msg is None:
            self.no_response()
        else:
            msg = cmsg.pack_msg(msg)
            if self.__to_all:
                self.send_message(message=msg, to=0, type=mtype, flush=True)
                self.__to_all = False
            else:
                self.send_message(message=msg, to=int(mxmsg.from_), type=mtype, flush=True)
        if launcher_msg is not None and self.launcher_sock is not None:
            self.logger.info('SENDING msg ' + launcher_msg.decode()[:100] + '[...]')
            send_msg(self.launcher_sock, launcher_msg)
            time.sleep(0.1)  # TODO - temporary kind-of bug fix...

    def _call_handler(self, mtype, message):
        if mtype == types.GET_CONFIG_PARAMS:
            return self.handle_get_config_params(message)
        elif mtype == types.REGISTER_PEER_CONFIG:
            return self.handle_register_peer_config(message)
        elif mtype == types.UNREGISTER_PEER_CONFIG:
            return self.handle_unregister_peer_config(message)
        elif mtype == types.UPDATE_PARAMS:
            msg, mtype, launcher_msg = self.handle_update_params(message)
            if mtype != types.CONFIG_ERROR:
                self.__to_all = True
            return msg, mtype, launcher_msg
        elif mtype == types.PEER_READY:
            return self.handle_peer_ready(message)
        elif mtype == types.PEERS_READY_QUERY:
            return self.handle_peers_ready_query(message)
        elif mtype == types.LAUNCHER_COMMAND:
            return self.handle_launcher_command(message)
        else:
            return None, None, None

    def handle_get_config_params(self, message_obj):
        param_owner = message_obj.receiver
        names = message_obj.param_names
        if param_owner == 'config_server':
            params = dict(experiment_uuid=self.exp_uuid)

        # elif param_owner not in self._configs:
        #     return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None
        else:
            # TODO error when param_name does not exist?
            # params = {}
            # for name in names:
            #     if name in self._configs[param_owner]:
            #         params[name] = self._configs[param_owner][name]
            params = self._get_params(param_owner, names)
            if isinstance(params, tuple):
                return params

        mtype = types.CONFIG_PARAMS
        msg = cmsg.fill_msg(mtype, sender=param_owner)
        cmsg.dict2params(params, msg)
        return msg, mtype, None

    def _get_params(self, param_owner, names, params=None):
        if params is None:
            params = {}
        self.logger.info("looking for %s, param names=%s" % (param_owner, str(names)))
        if param_owner not in self._configs:
            self.logger.info("%s not in %s" % (param_owner, str(self._configs)))
            return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None

        for name in names:
            if name in self._configs[param_owner]:
                params[name] = self._configs[param_owner][name]
            elif name in self._ext_configs[param_owner]:
                owner, name = self._ext_configs[param_owner][name]
                params = self._get_params(owner, [name], params)
        return params

    def handle_register_peer_config(self, message_obj):
        params = cmsg.params2dict(message_obj)
        ext_params = cmsg.params2dict(message_obj, field_name="ext_params")

        peer_id = message_obj.sender
        launcher_msg = None

        if peer_id in self._configs:
            mtype = types.CONFIG_ERROR
            msg = cmsg.fill_msg(mtype)
        else:
            self._configs[peer_id] = params
            self._ext_configs[peer_id] = ext_params
            mtype = types.PEER_REGISTERED
            msg = cmsg.fill_msg(mtype, peer_id=peer_id)
            launcher_msg = self.mtool.fill_msg('obci_peer_registered',
                                               peer_id=peer_id, params=params)
        self._save_config()
        return msg, mtype, launcher_msg

    def handle_unregister_peer_config(self, message_obj):
        self._configs.pop(message_obj.peer_id)

        if message_obj.peer_id in self._ready_peers:
            self._ready_peers.remove(message_obj.peer_id)
        self._save_config()
        return None, None, None  # TODO confirm unregister...

    def handle_update_params(self, message_obj):
        params = cmsg.params2dict(message_obj)
        param_owner = message_obj.sender
        if param_owner not in self._configs:
            launcher_msg = None
            return cmsg.fill_msg(types.CONFIG_ERROR,
                                 error_str="Peer unknown: {0}".format(param_owner)),\
                types.CONFIG_ERROR,\
                launcher_msg
        updated = {}
        for param in params:
            if param in self._configs[param_owner]:
                self._configs[param_owner][param] = params[param]
                updated[param] = params[param]

        if updated:
            mtype = types.PARAMS_CHANGED
            msg = cmsg.fill_msg(types.PARAMS_CHANGED, sender=param_owner)
            cmsg.dict2params(updated, msg)
            launcher_msg = self.mtool.fill_msg('obci_peer_params_changed',
                                               peer_id=param_owner, params=updated)
            self._save_config()
            return msg, mtype, launcher_msg
        return None, None, None

    def handle_peer_ready(self, message_obj):
        peer_id = message_obj.peer_id
        if peer_id not in self._configs:
            return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None
        self._ready_peers.append(peer_id)
        launcher_msg = self.mtool.fill_msg('obci_peer_ready', peer_id=peer_id)
        return message_obj, types.PEER_READY, launcher_msg

    def handle_peers_ready_query(self, message_obj):

        peer_id = message_obj.sender
        if peer_id not in self._configs:
            return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None

        green_light = True
        for dep in message_obj.deps:
            if dep not in self._ready_peers:
                green_light = False

        return cmsg.fill_msg(types.READY_STATUS,
                             receiver=peer_id, peers_ready=green_light), types.READY_STATUS, None

    def handle_launcher_command(self, message_obj):
        return None, None, message_obj.serialized_msg

    def _crash_extra_tags(self, exception=None):
        return {'obci_part': 'obci'}


if __name__ == "__main__":

    ConfigServer(settings.MULTIPLEXER_ADDRESSES).loop()

# TODO make doctests from this
"""
    srv = ConfigServer(settings.MULTIPLEXER_ADDRESSES)
    print "REGISTRATION"
    reg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender="ja", receiver="")

    cmsg.dict2params(dict(wr=1, dfg=[1,2,3,4,'zuzanna']), reg)
    srv.handle_register_peer_config(reg)

    reg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender="ty", receiver="")
    cmsg.dict2params(dict(a=1, bb=['ssdfsdf', 'LOL']), reg)
    srv.handle_register_peer_config(reg)

    reg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender="on", receiver="")
    cmsg.dict2params(dict(lll=0), reg)
    srv.handle_register_peer_config(reg)

    print srv._configs

    print "PEER_READY"
    rdy = cmsg.fill_msg(types.PEER_READY, peer_id="on")
    srv.handle_peer_ready(rdy)
    rdy = cmsg.fill_msg(types.PEER_READY, peer_id="ja")
    srv.handle_peer_ready(rdy)
    print srv._ready_peers

    print "PEERS_READY_QUERY"
    rdq = cmsg.fill_msg(types.PEERS_READY_QUERY, sender="ja", deps=["on, ty"])
    print srv.handle_peers_ready_query(rdq)[0]
    rdq = cmsg.fill_msg(types.PEERS_READY_QUERY, sender="ty", deps=["on"])
    print srv.handle_peers_ready_query(rdq)[0]

    print "GET_CONFIG_PARAMS"
    par = cmsg.fill_msg(types.GET_CONFIG_PARAMS, sender="ja", receiver="ty", param_names=['a','b'])
    print srv.handle_get_config_params(par)[0]
    par = cmsg.fill_msg(types.GET_CONFIG_PARAMS, sender="ja", receiver="ty", param_names=['bb'])
    rep = srv.handle_get_config_params(par)[0]
    print rep, "decoded params:\n", cmsg.params2dict(rep)

    print "DEREGISTRATION"
    unr = cmsg.fill_msg(types.UNREGISTER_PEER_CONFIG, peer_id="ja")
    srv.handle_unregister_peer_config(unr)
    print srv._configs
"""
