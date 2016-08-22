#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq


BASIC_MSG = dict(type='', sender='', receiver='', sender_ip='')
# BasicMessage = namedtuple('BasicMessage', 'type sender receiver')
# _basic_message = BasicMessage(type='basic_message', sender='', receiver='')

common_templates = {
    "rq_ok": dict(status='', request='', params=''),
    "rq_error": dict(err_code='', request='', details=''),
    "kill": dict(),
    "heartbeat": dict(),
    "ping": dict(),
    "pong": dict(),
    "pub_addr_rq": dict(),
    "pub_addr": dict(pub_addresses='', request='')
}

common_errors = ["invalid_msg_format",
                 "incomplete_message",
                 "unsupported_msg_type",
                 "no_pub_sock"]


class OBCIMessageTool(object):

    def __init__(self, msg_templates, errors=[]):
        self.templates = common_templates
        self.templates.update(msg_templates)
        self.errors = common_errors
        self.errors.append(errors)

    def add_templates(self, msg_templates):
        self.templates.update(msg_templates)

    def fill_msg(self, msg_type, **kwargs):
        if msg_type not in self.templates:
            raise OBCIMessageError()
        msg = self.templates[msg_type].copy()
        msg.update(BASIC_MSG)
        msg['type'] = msg_type

        for key, value in kwargs.items():
            if key not in msg:
                raise OBCIMessageError(
                    "Key {0} not defined for message {1}".format(
                        key, msg_type))
            msg[key] = value
        return json.dumps(msg).encode()

    def decode_msg(self, msg):
        return json.loads(msg.decode())

    def unpack_msg(self, msg):
        m = LauncherMessage()
        m.ParseFromString(msg)
        return m


class PollingObject(object):

    def __init__(self):
        self.poller = zmq.Poller()

    def poll_recv(self, socket, timeout):
        self.poller.register(socket, zmq.POLLIN)
        socks = None
        fail_det = None
        try:
            socks = dict(self.poller.poll(timeout=timeout))
        except zmq.ZMQError as e:
            fail_det = "obci_client: zmq.poll(): " + e.strerror
        finally:
            self.poller.unregister(socket)
            if socks is None:
                return None, fail_det

        if socket in socks and socks[socket] == zmq.POLLIN:
            return recv_msg(socket), None
        else:
            return None, "No data"


def send_msg(sock, message, flags=0):
    assert isinstance(message, bytes)
    return sock.send(message, flags=flags)


def recv_msg(sock, flags=0):
    return sock.recv(flags=flags)


class LauncherMessage(object):

    def SerializeToString(self):
        return json.dumps(vars(self)).encode()

    def __repr__(self):
        return str(self.dict())

    def raw(self):
        return json.dumps(vars(self), sort_keys=True, indent=4).encode()

    def ParseFromString(self, bytes):
        message = json.loads(bytes.decode())
        if not isinstance(message, dict):  # TODO more general keyed collection?
            raise OBCIMessageError()
        for key in message:
            setattr(self, key, message[key])

    def keys(self):
        return list(vars(self).keys())

    def dict(self):
        d = {}
        for attr, val in vars(self).items():
            d[attr] = val
        return d


class OBCIMessageError(Exception):
    pass
