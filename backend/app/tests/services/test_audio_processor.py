import asyncio
import contextlib
import os
import wave

import av
import numpy as np

from app.services import audio_processor

AUDIO_SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'audio_samples')
DUMMY_PCM_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm.wav')
DUMMY_OPUS_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_opus.opus')
DUMMY_PCM_RECOVERED_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm_recovered.wav')
DUMMY_PCM_RECOVERED_PATH_2 = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm_recovered_2.wav')


def test_opus_to_pcm() -> None:
    """Test Opus to PCM conversion"""
    if not os.path.exists(DUMMY_OPUS_PATH):
        # Skip test if dummy opus file doesn't exist
        return

    with open(DUMMY_OPUS_PATH, 'rb') as f:
        opus_data = f.read()
    pcm_data = audio_processor.opus_to_pcm(opus_data)
    assert isinstance(pcm_data, bytes)
    assert len(pcm_data) > 0


def test_pcm_to_opus() -> None:
    """Test PCM to Opus conversion"""
    if not os.path.exists(DUMMY_PCM_PATH):
        # Skip test if dummy pcm file doesn't exist
        return

    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    opus_data = audio_processor.pcm_to_opus(pcm_data)
    assert isinstance(opus_data, bytes)
    assert len(opus_data) > 0


def test_audio_stream_track() -> None:
    """Test AudioStreamTrack creation and basic functionality"""
    track = audio_processor.AudioStreamTrack()
    assert track.kind == 'audio'
    assert hasattr(track, 'recv')
    assert hasattr(track, 'add_frame')
    assert hasattr(track, 'queue')


def test_pcm_to_opus_and_back() -> None:
    """Test PCM to Opus conversion and back"""
    if not os.path.exists(DUMMY_PCM_PATH):
        # Skip test if dummy pcm file doesn't exist
        return

    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    opus_data = audio_processor.pcm_to_opus(pcm_data)
    recovered_pcm = audio_processor.opus_to_pcm(opus_data)

    # Compare the audio data (allowing for some compression loss)
    arr1 = np.frombuffer(pcm_data, dtype=np.int16)
    arr2 = np.frombuffer(recovered_pcm, dtype=np.int16)
    min_len = min(len(arr1), len(arr2))
    arr1 = arr1[:min_len]
    arr2 = arr2[:min_len]
    mse = np.mean((arr1 - arr2) ** 2)

    # Save recovered PCM for debugging
    os.makedirs(AUDIO_SAMPLE_DIR, exist_ok=True)
    with open(DUMMY_PCM_RECOVERED_PATH, 'wb') as f:
        f.write(recovered_pcm)

    assert mse < 10000


def test_resample_pcm_audio() -> None:
    """Test PCM audio resampling"""
    if not os.path.exists(DUMMY_PCM_PATH):
        # Create a simple test PCM data if file doesn't exist
        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        wave_data = np.sin(frequency * 2 * np.pi * t)
        pcm_data = (wave_data * 32767).astype(np.int16).tobytes()
        n_channels = 1
    else:
        with wave.open(DUMMY_PCM_PATH, 'rb') as wf:
            pcm_data = wf.readframes(wf.getnframes())
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
        assert sample_width == 2

    # Test resampling
    target_rate = sample_rate * 2 if sample_rate < 32000 else sample_rate // 2
    resampled = audio_processor.resample_pcm_audio(
        pcm_data, sample_rate, target_rate, channels=n_channels
    )

    assert isinstance(resampled, bytes)
    assert len(resampled) > 0

    # Check if the length ratio is approximately correct
    ratio = len(resampled) / len(pcm_data)
    expected_ratio = target_rate / sample_rate
    assert abs(ratio - expected_ratio) < 0.2

    # Save resampled audio for debugging
    os.makedirs(AUDIO_SAMPLE_DIR, exist_ok=True)
    with wave.open(DUMMY_PCM_RECOVERED_PATH_2, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(target_rate)
        wf.writeframes(resampled)


def test_resample_pcm_audio_gemini_format() -> None:
    """Test resampling to Gemini-required format (16kHz, mono, int16)"""
    # Create test audio data at 48kHz (common WebRTC rate)
    source_rate = 48000
    target_rate = 16000  # Gemini requirement
    duration = 0.5  # 0.5 seconds
    frequency = 440  # A4 note

    # Generate 48kHz mono audio
    samples = int(source_rate * duration)
    t = np.linspace(0, duration, samples, False)
    wave_data = np.sin(frequency * 2 * np.pi * t)
    pcm_data = (wave_data * 32767).astype(np.int16).tobytes()

    # Resample to Gemini format
    resampled = audio_processor.resample_pcm_audio(pcm_data, source_rate, target_rate, channels=1)

    # Verify output
    assert isinstance(resampled, bytes)
    assert len(resampled) > 0

    # Check the data format
    resampled_array = np.frombuffer(resampled, dtype=np.int16)
    assert resampled_array.dtype == np.int16  # 16-bit

    # Check length ratio
    ratio = len(resampled) / len(pcm_data)
    expected_ratio = target_rate / source_rate
    assert abs(ratio - expected_ratio) < 0.1


def test_is_silence() -> None:
    """Test silence detection"""
    # Test with actual silence (zeros)
    silence_data = np.zeros(1000, dtype=np.int16).tobytes()
    assert audio_processor.is_silence(silence_data)

    # Test with quiet audio (below threshold)
    quiet_data = (np.random.random(1000) * 100).astype(np.int16).tobytes()
    assert audio_processor.is_silence(quiet_data)

    # Test with loud audio (above threshold)
    loud_data = (np.random.random(1000) * 5000 + 1000).astype(np.int16).tobytes()
    assert not audio_processor.is_silence(loud_data)

    # Test with empty data
    assert audio_processor.is_silence(b'')


async def test_audio_stream_track_async() -> None:
    """Test AudioStreamTrack async functionality"""
    track = audio_processor.AudioStreamTrack()

    # Create a test audio frame
    sample_rate = 16000
    samples = 320  # 20ms at 16kHz
    audio_data = np.random.randint(-1000, 1000, samples, dtype=np.int16)

    # Create av.AudioFrame
    frame = av.AudioFrame.from_ndarray(audio_data.reshape(1, -1), format='s16', layout='mono')
    frame.sample_rate = sample_rate
    frame.pts = 0

    # Add frame to track
    await track.add_frame(frame)

    # Receive frame from track
    received_frame = await track.recv()
    assert received_frame is not None
    assert received_frame.sample_rate == sample_rate

    # Test stop signal
    await track.add_frame(None)
    with contextlib.suppress(asyncio.CancelledError):
        await track.recv()
