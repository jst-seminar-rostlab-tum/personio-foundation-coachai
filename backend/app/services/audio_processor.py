import asyncio
import io

import av
import numpy as np
from aiortc.mediastreams import MediaStreamTrack

OPUS_SAMPLE_RATE = 48000
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
CHANNELS = 1


class AudioStreamTrack(MediaStreamTrack):
    """
    Audio stream track that can be used to send audio data.
    This version is adapted for live streaming by using an internal queue.
    """

    kind = 'audio'

    def __init__(self) -> None:
        super().__init__()
        self.queue: asyncio.Queue[av.AudioFrame | None] = asyncio.Queue()

    async def recv(self) -> av.AudioFrame:
        """Pulls an audio frame from the queue to be sent to the client."""
        frame = await self.queue.get()
        if frame is None:
            # This is a signal to stop the track
            self.stop()
            raise asyncio.CancelledError
        return frame

    async def add_frame(self, frame: av.AudioFrame | None) -> None:
        """Adds a new audio frame (or a stop signal) to the queue."""
        await self.queue.put(frame)


def opus_to_pcm(opus_data: bytes, sample_rate: int = OPUS_SAMPLE_RATE) -> bytes:
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


def pcm_to_opus(pcm_data: bytes, sample_rate: int = OPUS_SAMPLE_RATE) -> bytes:
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


def resample_pcm_audio(
    pcm_data: bytes,
    source_sample_rate: int,
    target_sample_rate: int = SEND_SAMPLE_RATE,
    channels: int = CHANNELS,
) -> bytes:
    """
    Resample raw PCM audio data to a different sample rate

    Args:
        pcm_data: Raw PCM audio data (16-bit signed integers)
        source_sample_rate: Original sample rate
        target_sample_rate: Target sample rate, default 16000Hz (Gemini standard)
        channels: Number of audio channels, default 1 (mono)

    Returns:
        Resampled raw PCM audio data as bytes
    """
    if source_sample_rate == target_sample_rate:
        return pcm_data

    # Convert bytes to numpy array
    audio_array = np.frombuffer(pcm_data, dtype=np.int16)

    # Calculate number of samples per channel
    samples_per_channel = len(audio_array) // channels

    # Reshape correctly: (channels, samples_per_channel)
    if channels > 1:
        audio_array = audio_array.reshape(channels, samples_per_channel)
    else:
        # For mono, ensure we have the right shape (1, samples_per_channel)
        audio_array = audio_array.reshape(1, samples_per_channel)

    # Create audio frame
    input_frame = av.AudioFrame.from_ndarray(
        audio_array, format='s16', layout='mono' if channels == 1 else f'{channels}c'
    )
    input_frame.rate = source_sample_rate

    # Create resampler
    resampler = av.AudioResampler(
        format='s16', layout='mono' if channels == 1 else f'{channels}c', rate=target_sample_rate
    )

    # Resample
    output_frames = resampler.resample(input_frame)

    # Convert back to bytes
    if output_frames:
        output_array = output_frames[0].to_ndarray()
        return output_array.astype(np.int16).tobytes()
    else:
        return b''


def is_silence(audio_data: bytes, threshold: int = 500) -> bool:
    """
    Check if audio data is silence
    """
    if not audio_data:
        return True
    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float64)
    if not np.isfinite(audio_array).all():
        return True
    rms = np.sqrt(np.mean(audio_array**2))
    if not np.isfinite(rms):
        return True
    return rms < threshold
