
import time
from typing import List

from obci.core.peer import Peer
from obci.core.broker import Broker


def wait_for_peers(peers_list: List[Peer], broker: Broker, timeout: float=60.0) -> None:
    start_time = time.monotonic()
    while True:
        if (all(p._initialization_finished for p in peers_list) and
                len(broker._peers.keys()) == len(peers_list) + 1):
            break
        time.sleep(0.05)
        if time.monotonic() - start_time > timeout:
            raise Exception('wait_for_peers: timeout (={} seconds)'.format(timeout))


strings_list = [
    '', ' ', 'abc', '123', ' abc', ' 123', ' abc ', ' 123 ', '\n', '\r',
    '\a', '\b', '\f', '\t', '\v', '\'', '\"', '`', '\\', '/', '', '\x00', 'a\x00b',
    'ą, ć, ę, ł, ń, ó, ś, ź, ż, Ą, Ć, Ę, Ł, Ń, Ó, Ś, Ź, Ż', '⛱',
    'Ё Ђ Ѓ Є Ѕ І Ї Ј Љ Њ Ћ Ќ Ў Џ А Б В Г Д Е Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч'
    ' Ш Щ Ъ Ы Ь Э Ю Я а б в г д е ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я ё ђ'
    ' ѓ є ѕ і ї ј љ њ ћ ќ ў џ Ѡ ѡ Ѣ ѣ Ѥ ѥ Ѧ ѧ Ѩ ѩ Ѫ ѫ Ѭ ѭ Ѯ ѯ Ѱ ѱ Ѳ ѳ Ѵ ѵ Ѷ ѷ Ѹ ѹ Ѻ ѻ Ѽ ѽ'
    ' Ѿ ѿ Ҁ ҁ ҂ ҃ ...',
    '子曰：「學而時習之，不亦說乎？有朋自遠方來，不亦樂乎？人不知而不慍，不亦君子乎？」'
]

json_data = {
    'a': 1, 'b': 2, 'c': 'abc', 'd': 1.5,
    'f': {'a': 10, 'b': 11},
    'true': True, 'false': False,
    'null': None,
    'array_1': [1, 2, 3, 4],
    'array_1a': ['1', '2', '3', '4'],
    'array_2': [1.5, 2.5, 3.5, 4.5],
    'array_3': [{'a': 'a'}, {'b': 'b'}],
    'array_3a': [{'a': 'a'}, {'b': 'b'}, {'c': [1, 2, [3, 4], 5]}],
    'array_4': [1, 2, [3, 4], 5]
}

for i, string in enumerate(strings_list):
    json_data['unicode_{}'.format(i + 1)] = string
