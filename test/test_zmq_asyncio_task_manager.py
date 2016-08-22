#!/usr/bin/env python3

import asyncio
import logging
import threading
import time

import pytest

from obci.core.zmq_asyncio_task_manager import ZmqAsyncioTaskManager


WAIT_FOR_TASKS_DELAY = 0.5  # seconds
UNDER_TIMEOUT_DELAY = 0.1  # seconds
OVER_TIMEOUT_DELAY = 10.0  # seconds


class ZmqAsyncioTaskManagerWithName(ZmqAsyncioTaskManager):

    def __init__(self, *args, thread_name, **kwargs):
        self._thread_name = thread_name
        super().__init__(*args, **kwargs)


async def task1():
    thread = threading.current_thread()
    print("task 1 - '{}' ({})".format(thread.name, thread.ident))
    return 1


async def task2():
    global UNDER_TIMEOUT_DELAY
    await asyncio.sleep(UNDER_TIMEOUT_DELAY)
    thread = threading.current_thread()
    print("task 2 - '{}' ({})".format(thread.name, thread.ident))
    return 2


async def task3():
    global OVER_TIMEOUT_DELAY
    await asyncio.sleep(OVER_TIMEOUT_DELAY)
    thread = threading.current_thread()
    print("task 3 - '{}' ({})".format(thread.name, thread.ident))
    return 3


def all_mgr_threads_finished():
    return not any('Mgr_' in t.name for t in threading.enumerate())


def context_mgr_helper(iterations, force_shutdown_times):
    global WAIT_FOR_TASKS_DELAY
    for i in range(iterations):
        with ZmqAsyncioTaskManagerWithName(thread_name='Mgr_{}'.format(i)) as mgr:
            future1 = mgr.create_task(task1())
            future2 = mgr.create_task(task2())
            future3 = mgr.create_task(task3())
            time.sleep(WAIT_FOR_TASKS_DELAY)
            for _ in range(force_shutdown_times):
                mgr.shutdown()
                assert len(mgr._tasks) == 0
        assert future1.result() is 1
        assert future2.result() is 2
        with pytest.raises(asyncio.CancelledError):
            future3.result()
        assert all_mgr_threads_finished()


def test_context_manager():
    context_mgr_helper(iterations=1, force_shutdown_times=0)
    context_mgr_helper(iterations=1, force_shutdown_times=0)
    context_mgr_helper(iterations=5, force_shutdown_times=1)
    context_mgr_helper(iterations=5, force_shutdown_times=1)
    context_mgr_helper(iterations=1, force_shutdown_times=10)
    context_mgr_helper(iterations=1, force_shutdown_times=10)
    context_mgr_helper(iterations=5, force_shutdown_times=10)
    context_mgr_helper(iterations=5, force_shutdown_times=10)


def shutdown_helper(force_shutdown_times):
    global WAIT_FOR_TASKS_DELAY

    mgr = ZmqAsyncioTaskManagerWithName(thread_name='Mgr_X')
    future1 = mgr.create_task(task1())
    future2 = mgr.create_task(task2())
    future3 = mgr.create_task(task3())

    time.sleep(WAIT_FOR_TASKS_DELAY)

    for _ in range(force_shutdown_times):
        mgr.shutdown()
        assert len(mgr._tasks) == 0
        assert all_mgr_threads_finished()

    assert future1.result() is 1
    assert future2.result() is 2
    with pytest.raises(asyncio.CancelledError):
        future3.result()


def test_shutdown():
    shutdown_helper(force_shutdown_times=1)
    shutdown_helper(force_shutdown_times=1)
    shutdown_helper(force_shutdown_times=2)
    shutdown_helper(force_shutdown_times=2)
    shutdown_helper(force_shutdown_times=10)
    shutdown_helper(force_shutdown_times=10)


if __name__ == '__main__':
    # logging.root.setLevel(logging.DEBUG)
    logging.root.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    logging.root.addHandler(console)

    test_context_manager()
    test_shutdown()
