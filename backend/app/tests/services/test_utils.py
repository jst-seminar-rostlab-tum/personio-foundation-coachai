import numpy as np
from aiortc.mediastreams import MediaStreamTrack


class MockMediaStreamTrack(MediaStreamTrack):
    def __init__(self, kind: str = 'audio') -> None:
        super().__init__()
        self.kind = kind
        self._frames = []
        self._frame_index = 0

    def add_frame(self, frame: 'MockAudioFrame') -> None:
        self._frames.append(frame)

    async def recv(self) -> 'MockAudioFrame':
        if self._frame_index < len(self._frames):
            frame = self._frames[self._frame_index]
            self._frame_index += 1
            return frame
        import asyncio

        await asyncio.sleep(0.1)
        raise StopAsyncIteration


class MockAudioFrame:
    def __init__(self, rate: int = 48000, channels: int = 1, samples: int = 320) -> None:
        self.rate = rate
        self.channels = channels
        self.samples = samples

    def to_ndarray(self) -> np.ndarray:
        if self.channels == 1:
            return np.random.randint(-1000, 1000, size=self.samples, dtype=np.int16)
        else:
            return np.random.randint(
                -1000, 1000, size=(self.channels, self.samples), dtype=np.int16
            )
