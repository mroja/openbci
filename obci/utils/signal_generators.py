
import time
import random
import asyncio

import numpy as np

from obci.core.messages.protobuf_serializer import proto


MAX_VAL = 10
"""int: maximal value of saw signal"""


def saw_generator(max_val: int = MAX_VAL):
    """
    Saw signal generator.

    :param max_val: maximal value, after which generator drops to 0 and restarts
    """
    counter = 0
    while True:
        yield counter
        counter += 1
        if counter > max_val:
            counter = 0


class SawVerifier:
    """Raises exception if saw signal is not valid."""

    def __init__(self, max_val: int = MAX_VAL):
        super().__init__()
        self._saw_gen = saw_generator(max_val)

    def verify_next(self, value):
        assert next(self._saw_gen) == value


class AsyncSignalGenerator:

    def __init__(self):
        """
        Implements async generator for test signal.

        Following channels are generated:

        #. samples counter
        #. :func:`time.time` value
        #. :func:`time.monotonic` value
        #. always 0.0
        #. always 1.0
        #. always -1.0
        #. alternating sequence of 0 and 1
        #. 100 Hz sinus
        #. :func:`random.random` generated floats
        #. saw signal

        """
        super().__init__()
        self._last_time = None

        self._sampling_rate = 16.0
        self._samples_per_iteration = 4

        self._samples_delay = 1.0 / (self._sampling_rate / self._samples_per_iteration)

        self._stop = False

        self._samples_counter = 0
        self._last_flip = 0
        self._saw_gen = saw_generator()

    def __aiter__(self):
        return self

    async def __anext__(self) -> proto.SampleVector:
        if self._last_time is None:
            self._last_time = time.monotonic()
        sleep_duration = self._samples_delay - (time.monotonic() - self._last_time)
        # When we are late with the next sample sleep_duration is < 0. Despite being late call
        # asyncio.sleep(0) as it allows other, pending coroutines to be scheduled.
        if sleep_duration < 0:
            sleep_duration = 0
        await asyncio.sleep(sleep_duration)
        if self._stop:
            raise StopAsyncIteration
        self._last_time = time.monotonic()
        return proto.SampleVector(samples=[self._get_next_sample() for _ in range(self._samples_per_iteration)])

    def _get_next_sample(self) -> proto.Sample:
        sample = proto.Sample(timestamp=time.time(), channels=np.array([
            self._samples_counter,
            time.time(),
            time.monotonic(),
            0.0,
            1.0,
            -1.0,
            self._last_flip,
            np.sin(2.0 * np.pi * 100.0 * self._samples_counter / self._sampling_rate),  # 100 Hz sin
            random.random(),
            next(self._saw_gen)
        ], dtype=float))
        self._samples_counter += 1
        self._last_flip = 0 if self._last_flip == 1 else 1
        return sample
