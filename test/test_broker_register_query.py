#!/usr/bin/env python3

import asyncio
import logging

import pytest

from obci.core.broker import Broker
from obci.core.messages import Message
from obci.core.peer import (Peer,
                            PeerInitUrls,
                            TooManyRedirectsException,
                            MultiplePeersAvailable,
                            QueryAnswerUnknown)

from utils import wait_for_peers, json_data


class QueryAsyncPeer(Peer):

    async def _async1_query_handler(self, _: Message) -> Message:
        await asyncio.sleep(0)
        return Message('ASYNC1_QUERY', self.id, json_data)

    async def _async2_query_handler(self, _: Message) -> Message:
        await asyncio.sleep(0)
        return Message('ASYNC2_QUERY', self.id, json_data)

    async def initialization_finished(self):
        await super().initialization_finished()
        await self.register_query_handler_async('ASYNC1_QUERY', self._async1_query_handler)
        await self.register_query_handler_async('ASYNC2_QUERY', self._async2_query_handler)

    async def run_tests_coro(self):
        # answered by broker
        assert await self.query_async('1_QUERY') == 123
        assert await self.query_async('2_QUERY') == 'abc'
        assert await self.query_async('3_QUERY') == json_data

        # answered by single peer
        assert await self.query_async('Q1_QUERY') == json_data

        # answered by two peers
        with pytest.raises(MultiplePeersAvailable):
            await self.query_async('QA_QUERY')

        # redirect queries
        assert await self.query_async('REDIRECT_QUERY') == 'kjl'

        with pytest.raises(TooManyRedirectsException):
            assert await self.query_async('REDIRECT_LOOP_QUERY')

    async def unregister_q2_coro(self):
        await self.unregister_query_handler_async('ASYNC2_QUERY')

    async def unregister_all_coro(self):
        await self.unregister_query_handler_async()

    def run_tests(self):
        # will reraise exception if one was raised by run_tests_coro
        self.create_task(self.run_tests_coro()).exception()

    def unregister_q2(self):
        self.create_task(self.unregister_q2_coro()).exception()

    def unregister_all(self):
        self.create_task(self.unregister_all_coro()).exception()


def run_test(broker_rep,
             broker_xpub,
             broker_xsub,
             peer_pub,
             peer_rep,
             use_async_lambdas):

    broker = Broker([broker_rep], [broker_xpub], [broker_xsub])

    urls = PeerInitUrls(pub_urls=[peer_pub],
                        rep_urls=[peer_rep],
                        broker_rep_url=broker_rep)

    query1_peer = Peer(urls, '1')
    query2_peer = Peer(urls, '2')
    answer_peer = Peer(urls, '3')
    looper_peer = Peer(urls, '4')
    async_peer = QueryAsyncPeer(urls, '5')

    all_peers = [query1_peer, query2_peer, answer_peer, looper_peer, async_peer]

    wait_for_peers(all_peers, broker)

    def wrap_lambda(lambda_func):
        if use_async_lambdas:
            async def wrapper(*args, **kwargs):
                await asyncio.sleep(0)
                return lambda_func(*args, **kwargs)
            return wrapper
        else:
            return lambda_func

    # query types answered directly by broker
    broker.register_message_handler('1_QUERY', wrap_lambda(lambda _: Message('1_QUERY', '0', 123)))
    broker.register_message_handler('2_QUERY', wrap_lambda(lambda _: Message('2_QUERY', '0', 'abc')))
    broker.register_message_handler('3_QUERY', wrap_lambda(lambda _: Message('3_QUERY', '0', json_data)))

    def register_query_handler(peer, query_type):
        peer.register_query_handler(query_type, lambda _: Message(query_type, peer.id, json_data))

    # query types answered directly by single peer
    register_query_handler(query1_peer, 'Q1_QUERY')

    # query types answered directly by two peers
    register_query_handler(query1_peer, 'QA_QUERY')
    register_query_handler(query2_peer, 'QA_QUERY')

    url_answer_peer = answer_peer._rep_listening_urls[0]
    url_looper_peer = looper_peer._rep_listening_urls[0]

    # redirect query types
    query1_peer.register_query_handler(
        'REDIRECT_QUERY',
        lambda _: Message('REDIRECT_QUERY', query1_peer.id, 'kjl')
    )

    query1_peer.register_query_handler(
        'REDIRECT_LOOP_QUERY',
        lambda _: Message('REDIRECT', query1_peer.id, {'peers': [(query1_peer.id, url_looper_peer)]})
    )

    answer_peer.register_message_handler(
        'REDIRECT_QUERY',
        wrap_lambda(lambda _: Message('REDIRECT_QUERY', answer_peer.id, 'kjl')))

    answer_peer.register_message_handler(
        'REDIRECT_LOOP_QUERY',
        wrap_lambda(lambda _: Message('REDIRECT',
                                      answer_peer.id,
                                      {'peers': [(answer_peer.id, url_answer_peer)]})))

    looper_peer.register_message_handler(
        'REDIRECT_LOOP_QUERY',
        wrap_lambda(lambda _: Message('REDIRECT',
                                      looper_peer.id,
                                      {'peers': [(looper_peer.id, url_looper_peer)]})))

    # answered by broker
    assert query1_peer.query('1_QUERY') == 123
    assert query1_peer.query('2_QUERY') == 'abc'
    assert query1_peer.query('3_QUERY') == json_data

    # answered by single peer
    assert query1_peer.query('Q1_QUERY') == json_data

    # answered by two peers
    try:
        query1_peer.query('QA_QUERY')
    except MultiplePeersAvailable as ex:
        peer_urls = [url for _, url in ex.peers]
        assert set(peer_urls) <= set(query1_peer._rep_listening_urls + query2_peer._rep_listening_urls)
    else:
        assert False, 'Must throw exception.'

    # redirect queries
    assert query1_peer.query('REDIRECT_QUERY') == 'kjl'

    with pytest.raises(TooManyRedirectsException):
        query1_peer.query('REDIRECT_LOOP_QUERY')

    # test initial_peer parameter
    assert query1_peer.query('REDIRECT_QUERY', initial_peer=url_answer_peer) == 'kjl'

    with pytest.raises(TooManyRedirectsException):
        answer_peer.query('REDIRECT_LOOP_QUERY', initial_peer=url_looper_peer)

    with pytest.raises(TooManyRedirectsException):
        looper_peer.query('REDIRECT_LOOP_QUERY', initial_peer=url_answer_peer)

    # run tests from example peer
    async_peer.run_tests()
    assert query1_peer.query('ASYNC1_QUERY') == json_data
    assert query1_peer.query('ASYNC2_QUERY') == json_data

    async_peer.unregister_q2()
    assert query1_peer.query('ASYNC1_QUERY') == json_data
    with pytest.raises(QueryAnswerUnknown):
        query1_peer.query('ASYNC2_QUERY')

    async_peer.unregister_all()
    with pytest.raises(QueryAnswerUnknown):
        query1_peer.query('ASYNC1_QUERY')
    with pytest.raises(QueryAnswerUnknown):
        query1_peer.query('ASYNC2_QUERY')

    # test unregister_query_handler
    query1_peer.unregister_query_handler('REDIRECT_QUERY')
    query1_peer.unregister_query_handler('REDIRECT_LOOP_QUERY')

    with pytest.raises(QueryAnswerUnknown):
        query1_peer.query('REDIRECT_QUERY')
    with pytest.raises(QueryAnswerUnknown):
        query1_peer.query('REDIRECT_LOOP_QUERY')

    query2_peer.unregister_query_handler()

    assert query2_peer.query('QA_QUERY') == json_data
    assert query1_peer.query('QA_QUERY') == json_data

    # shutdown
    for p in all_peers:
        p.shutdown()

    broker.shutdown()


params = {
    'broker_rep': 'tcp://127.0.0.1:20001',
    'broker_xpub': 'tcp://127.0.0.1:20002',
    'broker_xsub': 'tcp://127.0.0.1:20003',
    'peer_pub': 'tcp://127.0.0.1:*',
    'peer_rep': 'tcp://127.0.0.1:*'
}


def test_query_1():
    params.update(use_async_lambdas=False)
    run_test(**params)


def test_query_2():
    params.update(use_async_lambdas=True)
    run_test(**params)


if __name__ == '__main__':
    # logging.root.setLevel(logging.DEBUG)
    logging.root.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    logging.root.addHandler(console)

    test_query_1()
    test_query_2()
