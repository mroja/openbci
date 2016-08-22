import asyncio
import time
from typing import List

import zmq


def bind_to_urls(socket, urls: List[str]) -> List[str]:
    """
    Bind socket to a given list of URLs. If duplicate URLs are given this function
    binds only once per URL. A unique list of real bound URLs is returned.

    :param zmq.Socket socket: ZMQ socket to bind
    :param list[str] urls: list of URLs to bind to
    :return: list of real bounded URLs
    """
    listening_urls = set()
    for url in list(set(urls)):
        socket.bind(url)
        real_url = socket.getsockopt(zmq.LAST_ENDPOINT)
        if real_url:
            listening_urls.add(real_url.decode())
    return list(listening_urls)


class TimeoutException(Exception):
    """
    Raised by `recv_multipart_with_timeout` when timeout is reached.
    """


async def recv_multipart_with_timeout(socket,
                                      timeout: float=1.0,
                                      sleep_interval: float=0.01
                                      ) -> bytes:
    """
    This wrapper exists because of a bug in socket.recv_multipart function
    (zmq.asyncio sockets ignore RCVTIMEO option).
    For more information see: https://github.com/zeromq/pyzmq/issues/825.
    """
    start_time = time.monotonic()
    while True:
        try:
            response = await socket.recv_multipart(zmq.NOBLOCK)
            return response
        except zmq.error.Again:
            if time.monotonic() - start_time > timeout:
                raise TimeoutException()
            await asyncio.sleep(sleep_interval)
