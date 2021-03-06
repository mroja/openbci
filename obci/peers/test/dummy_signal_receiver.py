
import time
import numpy as np

from obci.core.peer import Peer
from obci.core.messages import Message
from obci.utils.signal_generators import saw_generator

from obci.core.messages.protobuf_serializer import proto


class DummySignalReceiverPeer(Peer):
    """
    Signal receiver peer receives signal generated by `DummyAmplifierPeer`,
    verifies its correctness and send another signal consisting of received
    signal mean across channels and saw.
    """

    def __init__(self, *args, generator_peer_name='Generator', **kwargs):
        super().__init__(*args, **kwargs)
        self._saw_gen = saw_generator()
        self._samples_counter = 0
        self._generator_peer_name = generator_peer_name

    async def initialization_finished(self):
        await super().initialization_finished()
        self.register_message_handler('SampleVector', self.handle_signal_message)
        self.set_filter('SampleVector', self._generator_peer_name)

    async def handle_signal_message(self, msg):
        new_samples = []
        for d in msg.data.samples:
            new_samples.append(proto.Sample(timestamp=time.time(),
                                            channels=[self._samples_counter,
                                                      np.sum(d.channels) / len(d.channels),
                                                      next(self._saw_gen)]))
            self._samples_counter += 1
        return Message('SampleVector', self.id, proto.SampleVector(samples=new_samples))
