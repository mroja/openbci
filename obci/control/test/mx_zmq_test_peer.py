#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from obci.mx_legacy.multiplexer_constants import peers, types
from obci.configs import settings

from obci.control.test.zmq_mx_test import SEND

from obci.control.peer.configured_client import ConfiguredClient
import obci.control.common.config_message as cmsg


class TestClient2(ConfiguredClient):

    def __init__(self, addresses):
        super(TestClient2, self).__init__(addresses=addresses, type=peers.CONFIGURER)
        self.ready()
        print("[mx client] connected :)")

    def test(self):

        req = cmsg.fill_msg(types.GET_CONFIG_PARAMS,
                            sender='aaa',
                            param_names=['a'],
                            receiver='')
        received = 0
        for i in range(SEND):
            msg = self.__query(self.conn, req, types.DICT_GET_REQUEST_MESSAGE)
            if msg is None:
                print(":(((")
                continue

            if int(msg.message) == received + 1:
                received += 1
            if received % 10000 == 0:
                print("made ", received, "queries")

        if received == SEND:
            print("[mx peer...] OK")
        else:
            print("[mx peer...] WUT?", received)

        self.set_param('ach', '567')

    def __query(self, conn, msg, msgtype):
        try:
            reply = conn.query(message=msg,
                               type=msgtype)
        except Exception as ex:
            print("Query failed: {}".format(ex))
            reply = None
        return reply


if __name__ == "__main__":
    srv = TestClient2(settings.MULTIPLEXER_ADDRESSES)
    srv.test()
