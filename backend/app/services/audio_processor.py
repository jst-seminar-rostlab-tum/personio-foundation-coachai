import asyncio
import io
import os
import wave

import av
import numpy as np
import webrtcvad
from aiortc.mediastreams import MediaStreamTrack

OPUS_SAMPLE_RATE = 48000
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
CHANNELS = 1

# VAD instance (global shared)
vad = webrtcvad.Vad(1)  # 0-3, 3 is high sensitivity


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


# NOTE:
# When using aiortc, the audio frames you receive (via frame.to_ndarray())
# are already decoded PCM (int16).
# You can use them directly—there is NO NEED to manually
# convert between Opus and PCM in your main WebRTC pipeline!
# Only use these conversion functions for file processing, offline transcoding,
# or special cases.
# For real-time WebRTC audio, always use PCM end-to-end to avoid audio corruption
# and compatibility issues.


def opus_to_pcm(opus_data: bytes, sample_rate: int = OPUS_SAMPLE_RATE) -> bytes:
    """
    Convert Opus data to PCM data

    Args:
        opus_data: Raw Opus encoded audio data
        sample_rate: Sample rate, default 48000Hz (WebRTC standard)

    Returns:
        PCM audio data as bytes

    WARNING:
        - In aiortc, received audio frames are already decoded PCM (int16).
          You should use them directly—do NOT manually convert between Opus and PCM!
        - Only use this function for file processing, offline transcoding, or special scenarios.
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


# NOTE:
# When using aiortc, the audio frames you receive (via frame.to_ndarray())
# are already decoded PCM (int16).
# You can use them directly—there is NO NEED to manually
# convert between Opus and PCM in your main WebRTC pipeline!
# Only use these conversion functions for file processing, offline transcoding,
# or special scenarios.
# For real-time WebRTC audio, always use PCM end-to-end to avoid audio corruption
# and compatibility issues.


def pcm_to_opus(pcm_data: bytes, sample_rate: int = OPUS_SAMPLE_RATE) -> bytes:
    """
    Convert PCM data to Opus data

    Args:
        pcm_data: Raw PCM audio data
        sample_rate: Sample rate, default 48000Hz (WebRTC standard)

    Returns:
        Opus encoded audio data as bytes

    WARNING:
        - In aiortc, received audio frames are already decoded PCM (int16).
          You should use them directly—do NOT manually convert between Opus and PCM!
        - Only use this function for file processing, offline transcoding, or special scenarios.
        - For real-time WebRTC audio, always use PCM end-to-end to avoid
            audio corruption and compatibility issues.
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


def is_silence(audio_data: bytes, sample_rate: int = SEND_SAMPLE_RATE) -> bool:
    """
    Check if audio data contains speech using WebRTC VAD

    Args:
        audio_data: Raw PCM audio data (16-bit signed integers)
        sample_rate: Sample rate of the audio data (8000, 16000, 32000, or 48000)

    Returns:
        True if no speech detected (silence), False if speech detected
    """
    if not audio_data:
        return True

    # webrtcvad only supports specific sample rates
    supported_rates = [8000, 16000, 32000, 48000]
    # if the sample rate is not supported, use energy detection
    if sample_rate not in supported_rates:
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        if not np.isfinite(audio_array).all():
            return True
        rms = np.sqrt(np.mean(audio_array**2))
        if not np.isfinite(rms):
            return True
        return rms < 500

    # webrtcvad requires specific frame durations (10ms, 20ms, or 30ms)
    frame_duration_ms = 20  # use 20ms frames
    frame_size = int(sample_rate * frame_duration_ms / 1000)
    bytes_per_frame = frame_size * 2  # 16-bit = 2 bytes per sample

    # if data length is less than one frame, consider it silence
    if len(audio_data) < bytes_per_frame:
        return True

    # only process the first frame (if there are multiple frames, loop through them)
    frame_data = audio_data[:bytes_per_frame]

    try:
        # webrtcvad.is_speech returns True if there is speech, False if silence
        has_speech = vad.is_speech(frame_data, sample_rate)
        return not has_speech  # is_silence returns True if silence
    except Exception:
        # if VAD processing fails, fall back to simple energy detection
        audio_array = np.frombuffer(frame_data, dtype=np.int16).astype(np.float32)
        if not np.isfinite(audio_array).all():
            return True
        rms = np.sqrt(np.mean(audio_array**2))
        if not np.isfinite(rms):
            return True
        return rms < 500


def has_voice(audio_data: bytes, sample_rate: int = SEND_SAMPLE_RATE) -> bool:
    """
    Check if audio data contains speech using WebRTC VAD

    Args:
        audio_data: Raw PCM audio data (16-bit signed integers)
        sample_rate: Sample rate of the audio data

    Returns:
        True if speech detected, False if silence
    """
    return not is_silence(audio_data, sample_rate)


AUDIO_CHUNK_DIR = 'audio_chunks'


def save_pcm_audio_to_wav(
    pcm_data: bytes,
    file_path: str,
    sample_rate: int = SEND_SAMPLE_RATE,
    channels: int = CHANNELS,
    sampwidth: int = 2,
    append: bool = False,
) -> None:
    """
    Save PCM audio data to a WAV file.

    Args:
        pcm_data: Raw PCM audio data (16-bit)
        file_path: Path to save the WAV file
        sample_rate: Sample rate, default 16000
        channels: Number of channels, default 1
        sampwidth: Sample width in bytes, default 2 (16-bit)
        append: Whether to append to the file (True) or overwrite (False)
    """
    if not os.path.exists(AUDIO_CHUNK_DIR):
        os.makedirs(AUDIO_CHUNK_DIR)
    mode = 'ab' if append else 'wb'
    with wave.open(os.path.join(AUDIO_CHUNK_DIR, file_path), mode) as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
