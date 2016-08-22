from typing import Optional

import zmq
import zmq.asyncio

from obci.core import OBCI_DEBUG
from .asyncio_task_manager import AsyncioTaskManager


class ZmqAsyncioTaskManager(AsyncioTaskManager):

    @staticmethod
    def new_event_loop() -> zmq.asyncio.ZMQEventLoop:
        """
        Overloaded function to create ZMQEventLoop instances.

        Returns:
            new instance if ZMQEventLoop
        """
        loop = zmq.asyncio.ZMQEventLoop()
        if OBCI_DEBUG:
            loop.set_debug(True)
        return loop

    _thread_name = 'ZmqAsyncioTaskManager'
    _logger_name = 'ZmqAsyncioTaskManager'

    def __init__(self,
                 asyncio_loop: Optional[zmq.asyncio.ZMQEventLoop]=None,
                 zmq_context: Optional[zmq.asyncio.Context]=None,
                 zmq_io_threads: int=1
                 ) -> None:
        """
        Adds ZMQ context management to `AsyncioTaskManager`.

        :param asyncio_loop: existing message loop or `None` if new message loop should be created
        :param zmq_context: existing asyncio ZMQ context or `None` if new context should be created
        :param zmq_io_threads: number if ZMQ I/O threads
        """
        assert zmq_context is None or isinstance(zmq_context, zmq.asyncio.Context)

        super().__init__(asyncio_loop)

        self._zmq_io_threads = zmq_io_threads
        if zmq_context is None:
            self._owns_ctx = True
            self._ctx = zmq.asyncio.Context(io_threads=self._zmq_io_threads)
        else:
            self._owns_ctx = False
            self._ctx = zmq_context

    @property
    def owns_zmq_context(self) -> bool:
        """True if ZMQ context is owned by this object."""
        return self._owns_ctx

    def _cleanup(self) -> None:
        """
        If this class owns ZMQ context remember to close all
        sockets before calling this function through `super()._cleanup()`.
        """
        if self._owns_ctx:
            self._ctx.destroy(linger=0)
            self._ctx = None
        super()._cleanup()
