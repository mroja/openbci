#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import time

from obci.control.common.message import OBCIMessageTool, send_msg
from obci.control.launcher.launcher_messages import message_templates
from obci.control.launcher.obci_client import OBCIClient

import obci.control.launcher.launcher_logging as logger
from obci.control.peer import peer_cmd
from obci.control.peer.config_defaults import CONFIG_DEFAULTS

LOGGER = logger.get_logger("start_eeg_signal", "info")


def start_eeg_signal_experiment(ctx, srv_addrs, rq_message):
    client = OBCIClient(srv_addrs, ctx)
    # server_req_socket = ctx.socket(zmq.REQ)
    #     for addr in srv_addrs:
    #         server_req_socket.connect(addr)

    amp_params = {}
    amp_params.update(rq_message.amplifier_params['additional_params'])
    del rq_message.amplifier_params['additional_params']
    amp_params.update(rq_message.amplifier_params)

    par_list = ['--peer', 'amplifier']
    for par, val in amp_params.items():
        par_list += ['-p', par, str(val)]
    for par, val in CONFIG_DEFAULTS.items():
        if par not in par_list:
            par_list += ['-p', par, str(val)]

    overwrites = peer_cmd.peer_overwrites_pack(par_list)
    result = client.launch(rq_message.launch_file, None, rq_message.name, overwrites)

    LOGGER.info("START EEG signal! return to:  " + rq_message.client_push_address)
    mtool = OBCIMessageTool(message_templates)
    to_client = ctx.socket(zmq.PUSH)
    to_client.connect(rq_message.client_push_address)
    if result is None or result.type == 'no_data':
        send_msg(to_client, mtool.fill_msg("rq_error", err_code="launch_failed",
                                           details="No response from server or experiment"))
    else:
        send_msg(to_client, result.raw())
    LOGGER.info("sent eeg launch result" + str(result)[:500])
    time.sleep(0.1)
