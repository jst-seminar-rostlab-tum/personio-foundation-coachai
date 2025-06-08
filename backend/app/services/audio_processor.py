import io

import av
import numpy as np
from aiortc.mediastreams import MediaStreamTrack


class AudioStreamTrack(MediaStreamTrack):
    """Audio stream track that can be used to send audio data"""

    kind = 'audio'

    def __init__(self, audio_data: bytes, sample_rate: int = 48000) -> None:
        """
        :param audio_data: PCM audio data
        :param sample_rate: Sample rate, default 48000Hz (WebRTC standard)
        """
        super().__init__()
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self._timestamp = 0

    async def recv(self) -> av.AudioFrame:
        """Receive audio frame"""
        # Create audio frame from bytes
        audio_array = np.frombuffer(self.audio_data, dtype=np.int16)

        # Create frame
        frame = av.AudioFrame.from_ndarray(
            audio_array.reshape(-1, 1),  # Reshape to (samples, channels=1)
            format='s16',
            layout='mono',
        )
        frame.pts = self._timestamp
        frame.rate = self.sample_rate
        frame.time_base = f'1/{self.sample_rate}'

        # Update timestamp
        self._timestamp += len(audio_array)

        return frame


def opus_to_pcm(opus_data: bytes, sample_rate: int = 48000) -> bytes:
    """
    Convert Opus data to PCM data

    Args:
        opus_data: Raw Opus encoded audio data
        sample_rate: Sample rate, default 48000Hz (WebRTC standard)

    Returns:
        PCM audio data as bytes
    """
    # Create memory file objects
    input_container = av.open(io.BytesIO(opus_data), format='opus')
    output_buffer = io.BytesIO()
    output_container = av.open(output_buffer, format='wav', mode='w')
    # Set output stream parameters
    stream = output_container.add_stream('pcm_s16le', rate=sample_rate)

    # Decode and write
    for frame in input_container.decode(audio=0):
        for packet in stream.encode(frame):
            output_container.mux(packet)

    output_container.close()
    return output_buffer.getvalue()


def pcm_to_opus(pcm_data: bytes, sample_rate: int = 48000) -> bytes:
    """
    Convert PCM data to Opus data

    Args:
        pcm_data: Raw PCM audio data
        sample_rate: Sample rate, default 48000Hz (WebRTC standard)

    Returns:
        Opus encoded audio data as bytes
    """
    # Create memory file objects
    input_container = av.open(io.BytesIO(pcm_data), format='wav')
    output_buffer = io.BytesIO()
    output_container = av.open(output_buffer, format='opus', mode='w')
    # Set output stream parameters
    stream = output_container.add_stream('opus', rate=sample_rate)

    # Encode and write
    for frame in input_container.decode(audio=0):
        for packet in stream.encode(frame):
            output_container.mux(packet)

    output_container.close()
    return output_buffer.getvalue()


def resample_audio(
    audio_data: bytes, source_sample_rate: int, target_sample_rate: int = 48000
) -> bytes:
    """
    Resample audio data to a different sample rate

    Args:
        audio_data: Raw PCM audio data
        source_sample_rate: Original sample rate
        target_sample_rate: Target sample rate, default 48000Hz (WebRTC standard)

    Returns:
        Resampled PCM audio data as bytes
    """
    if source_sample_rate == target_sample_rate:
        return audio_data

    # Create memory file objects
    input_container = av.open(io.BytesIO(audio_data), format='wav')
    output_buffer = io.BytesIO()
    output_container = av.open(output_buffer, format='wav', mode='w')
    # Set output stream parameters
    stream = output_container.add_stream('pcm_s16le', rate=target_sample_rate)

    # Resample and write
    for frame in input_container.decode(audio=0):
        for packet in stream.encode(frame):
            output_container.mux(packet)

    output_container.close()
    return output_buffer.getvalue()
