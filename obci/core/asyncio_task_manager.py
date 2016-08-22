
import asyncio
import logging
import threading
import functools
import concurrent.futures
import types
from typing import Optional, Union, Callable, Any

from obci.core import OBCI_DEBUG


class MessageLoopRunningException(Exception):
    """
    Raised when function requiring to be called from outside message loop was
    called from inside message loop.
    """


def ensure_not_inside_msg_loop(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator used by AsyncioTaskManager and its subclasses to annotate methods
    requiring to be called outside message loop.
    """
    @functools.wraps(func)
    def _wrapper(self, *args, **kwargs):
        if self._loop == asyncio.get_event_loop() and self._loop.is_running():
            raise MessageLoopRunningException('Function was called inside running message loop. '
                                              'Probably you wanted to use the async version of called function.')
        return func(self, *args, **kwargs)
    return _wrapper


class AsyncioTaskManager:

    @staticmethod
    def new_event_loop() -> asyncio.BaseEventLoop:
        """
        When AsyncioTaskManager runs with self.owns_asyncio_loop == True
        this function is called to create a new asyncio event loop.

        Default implementation returns :func:`asyncio.new_event_loop`.

        :return: event loop object
        """
        loop = asyncio.new_event_loop()
        if OBCI_DEBUG:
            loop.set_debug(True)
        return loop

    _thread_name = 'AsyncioTaskManager'
    _logger_name = 'AsyncioTaskManager'

    def __init__(self,
                 asyncio_loop: Optional[asyncio.BaseEventLoop]=None
                 ) -> None:

        """
        AsyncioTaskManager class is used to manage a set of tasks.

        Tasks are created using `create_task` function.


        Examples:
            Can be used as context manager::

                with AsyncioTaskManager() as mgr:
                    pass

            Or as async context manager::

                async with AsyncioTaskManager() as mgr:
                    pass

        :param asyncio_loop: existing message loop or `None` if new message loop should be created
        """
        assert asyncio_loop is None or isinstance(asyncio_loop, asyncio.BaseEventLoop)

        super().__init__()

        self._logger = logging.getLogger(self._logger_name)
        self._tasks = set()
        self._shutdown_lock = threading.Lock()
        self._tasks_lock = threading.Lock()
        self._cancel_tasks_finished = threading.Condition(threading.Lock())
        self._create_task_enabled = True
        if asyncio_loop is not None:
            self._owns_loop = False
            self._loop = asyncio_loop
            self._thread = None
        else:
            self._owns_loop = True
            self._loop = self.new_event_loop()
            self._thread = threading.Thread(target=self.__thread_func,
                                            name=self._thread_name)
            self._thread.daemon = True
            self._thread.start()

    def __del__(self):
        """
        When running with 'self._owns_loop == True'
        this function requires 'self._thread.daemon == True',
        otherwise thread will not end properly when program ends
        and this function won't be called by Python.
        """
        self.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    async def __aenter__(self):
        assert self._loop is not None
        assert asyncio.get_event_loop() == self._loop
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_shutdown()

    @property
    def owns_asyncio_loop(self) -> bool:
        """ bool: True if owns asyncio message loop.

        If this instance owns message loop, it will be closed and destroyed
        on `AsyncioTaskManager`'s shutdown.
        """
        return self._owns_loop

    def create_task(self,
                    coro: types.CoroutineType
                    ) -> Union[asyncio.Future, concurrent.futures.Future]:
        """
        Create a new task and return Future object.

        New task will be added to an internal tasks list. When task finishes or
        raises exception or is cancelled it will be automatically removed from
        that list. When `AsyncioTaskManager` is asked to close it will cancel
        all tasks on that list.

        .. note::
            Can be called from any thread or/and from any coroutine.
        """
        assert self._loop is not None

        if not self._create_task_enabled:
            raise Exception('AsyncioTaskManager is shutting down. Creating new tasks disabled.')

        async def coro_wrapper():
            nonlocal coro
            try:
                return await coro
            except asyncio.CancelledError:
                self._logger.info('Coroutine cancelled: {}'.format(coro))
                raise
            except Exception:
                self._logger.info('Exception in coroutine: {}'.format(coro), exc_info=True)
                raise

        if asyncio.get_event_loop() == self._loop:
            future = asyncio.ensure_future(coro_wrapper(), loop=self._loop)
        else:
            future = asyncio.run_coroutine_threadsafe(coro_wrapper(), loop=self._loop)

        with self._tasks_lock:
            self._tasks.add(future)

        def future_done_callback(future_obj):
            if future_obj in self._tasks:
                with self._tasks_lock:
                    self._tasks.remove(future_obj)

        future.add_done_callback(future_done_callback)

        return future

    @ensure_not_inside_msg_loop
    def shutdown(self) -> None:
        """
        Can be called from ANY thread, but NOT from event loop.
        It will block until all pending tasks are finished.
        Can be called multiple times.
        """
        with self._shutdown_lock:
            if not self._create_task_enabled:
                assert len(self._tasks) == 0
                return
            self._create_task_enabled = False
            if self._owns_loop:
                if self._thread.is_alive() and self._loop.is_running:
                    self._loop.call_soon_threadsafe(self._loop.stop)
                self._thread.join()
            else:
                if self._loop.is_running:
                    asyncio.run_coroutine_threadsafe(self.__cancel_all_tasks(notify=True), loop=self._loop)
                    self._cancel_tasks_finished.wait()
        assert len(self._tasks) == 0

    async def async_shutdown(self) -> None:
        """
        Can be called from coroutine running inside message loop.
        """
        self._create_task_enabled = False
        await self.__cancel_all_tasks(notify=False)

    def _cleanup(self) -> None:
        """
        Can be reimplemented to perform extra cleanup tasks.

        .. note::
            Always remember to call `super()._cleanup()` when overloading this function.
        """
        pass

    async def __cancel_all_tasks(self, notify: bool) -> None:
        """
        Cancel all pending tasks and wait for them to finish.
        """
        try:
            gather_future = asyncio.gather(*self._tasks)
            gather_future.cancel()
            await asyncio.wait_for(gather_future, None, loop=self._loop)
        finally:
            try:
                self._cleanup()
            finally:
                if notify:
                    self._cancel_tasks_finished.notify_all()

    def __thread_func(self) -> None:
        """
        Entry point of message loop thread. Runs new message loop in a new thread when self.owns_asyncio_loop is True.
        """
        assert self._owns_loop and self._loop is not None and self._thread is not None
        try:
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Setting message loop for thread '{}' ({})."
                                   .format(self._thread.name, self._thread.ident))
            asyncio.set_event_loop(self._loop)
            self._logger.debug('Starting message loop...')
            self._loop.run_forever()
        except Exception:
            self._logger.exception('Exception in asyncio event loop:')
        finally:
            self._create_task_enabled = False
            self._logger.debug('Message loop stopped. Cancelling all pending tasks.')
            try:
                tasks = asyncio.gather(*asyncio.Task.all_tasks(),
                                       loop=self._loop,
                                       return_exceptions=True)
                tasks.cancel()
                try:
                    self._loop.run_until_complete(tasks)
                except asyncio.CancelledError:
                    self._logger.debug('cancelled: {}'.format(tasks), exc_info=True)
                    pass
                except Exception:
                    self._logger.exception('Exception during message loop shutdown phase:')
                    raise
                finally:
                    self._loop.close()
            except Exception:
                self._logger.exception('Unknown exception during message loop shutdown phase:')
            finally:
                self._cleanup()
                self._logger.debug('All cleanup tasks finished. Event loop thread will end now.')
