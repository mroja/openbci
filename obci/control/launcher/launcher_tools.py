#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path

NOT_READY = 'not_ready'
READY_TO_LAUNCH = 'ready_to_launch'
LAUNCHING = 'launching'
FAILED_LAUNCH = 'failed_launch'
RUNNING = 'running'
FINISHED = 'finished'
FAILED = 'failed'
TERMINATED = 'terminated'

EXP_STATUSES = [NOT_READY, READY_TO_LAUNCH, LAUNCHING,
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED]

POST_RUN_STATUSES = [FINISHED, FAILED, TERMINATED, FAILED_LAUNCH]
RUN_STATUSES = [LAUNCHING, RUNNING]


class ExperimentStatus(object):

    def __init__(self):
        self.status_name = NOT_READY
        self.details = {}
        self.peers_status = {}

    def set_status(self, status_name, details={}):
        self.status_name = status_name
        self.details = details

    def as_dict(self):
        d = dict(status_name=self.status_name,
                 details=self.details,
                 peers_status={})
        for peer_id, st in self.peers_status.items():
            d['peers_status'][peer_id] = st.as_dict()
        return d

    def peer_status(self, peer_id):

        return self.peers_status.get(peer_id, None)

    def peer_status_exists(self, status_name):
        return status_name in [st.status_name for st in list(self.peers_status.values())]

    def del_peer_status(self, peer_id):
        del self.peers_status[peer_id]


class PeerStatus(object):

    def __init__(self, peer_id, status_name=NOT_READY):
        self.peer_id = peer_id
        self.status_name = status_name
        self.details = {}

    def set_status(self, status_name, details=()):
        self.status_name = status_name
        self.details = details

    def as_dict(self):
        return dict(peer_id=self.peer_id, status_name=self.status_name,
                    details=self.details)


def obci_root():
    path = os.path.realpath(os.path.dirname(__file__))
    path = os.path.split(path)[0]
    path = os.path.split(path)[0]
    return path


def obci_root_relative(path):
    _path = path
    if path:
        print("---- ", path)
        root = obci_root()
        if os.path.commonprefix([path, root]).startswith(root):
            _path = path[len(root):]
            if _path.startswith('/') or _path.startswith('\\'):
                _path = _path[1:]
    return _path


def broker_path():
    """ Used only in obci_process_supervisor.py and supervisor_test.py """
    if which('obci_broker'):
        return which('obci_broker')
    else:
        return os.path.join(obci_root(), 'bin', 'obci_broker')


def module_path(module):
    path = module.__file__
    path = '.'.join([path.rsplit('.', 1)[0], 'py'])
    return os.path.normpath(path)


def default_config_path(peer_program_path):
    file_endings = ['py', 'java', 'jar', 'class', 'exe', 'sh', 'bin']
    base = peer_program_path
    sp = peer_program_path.rsplit('.', 1)
    if len(sp) > 1:
        if len(sp[1]) < 3 or sp[1] in file_endings:
            base = sp[0]
    conf_path = expand_path(base + '.ini')
    if os.path.exists(conf_path):
        return conf_path
    else:
        return ''


def expand_path(program_path, base_dir=None):
    if base_dir is None:
        base_dir = obci_root()
    if not program_path:
        return program_path
    program_path = os.path.normpath(program_path)
    p = os.path.expanduser(program_path)
    obcip = os.path.realpath(os.path.join(base_dir, p))
    if os.path.isabs(p) and os.path.exists(p):
        return p
    elif os.path.exists(obcip):
        return obcip
    elif which(p):
        return which(p)
    else:
        return program_path


def which(file):
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
            return os.path.join(path, file)
    return None

if __name__ == '__main__':
    print(obci_root())
