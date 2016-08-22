#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq

from obci.control.common.message import send_msg, recv_msg

SEND = 1000000


class Tester(object):

    def __init__(self):
        self.ctx = zmq.Context()

        # self.push = self.ctx.socket(zmq.PUSH)
        # self.push.bind('tcp://*:17890')
        # self.push.setsockopt(zmq.LINGER, 0)

        self.pull = self.ctx.socket(zmq.PULL)
        self.pull.bind('tcp://*:16789')
        self.pull.setsockopt(zmq.LINGER, 0)
        # self.pull.setsockopt(zmq.SUBSCRIBE, "")

    def test(self):
        # for i in range(SEND):
        #     send_msg(self.push, str(i))
        print("zmq client --- start receiving")
        received = 0
        prev = -1
        for i in range(SEND):
            msg = recv_msg(self.pull)
            if int(msg):
                # prev = int(msg)
                received += 1
            if received % 10000 == 0:
                print("zmq: received ", received, "messages, last: ", msg)

        if received == SEND:
            print("zmq: OK")
        else:
            print("OHHHH NOOOOOOOOO :( :( :( :( :(", received)
        # self.push.close()
        self.pull.close()

        print("zmq: finished.")

if __name__ == '__main__':
    t = Tester()
    t.test()
