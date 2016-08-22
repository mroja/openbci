
from obci.core.messages import Message
from obci.core.peer import Peer

from obci.utils.signal_generators import AsyncSignalGenerator


class DummyAmplifierPeer(Peer):
    """
    Amplifier peer generates signal using AsyncSignalGenerator.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def initialization_finished(self):
        await super().initialization_finished()
        self.create_task(self.generate_test_signal())

    async def generate_test_signal(self):
        sig_gen = AsyncSignalGenerator()
        async for samples in sig_gen:
            await self.send_message(Message('SampleVector', self.id, samples))
