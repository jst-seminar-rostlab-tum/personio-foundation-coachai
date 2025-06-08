import os

import numpy as np

from app.services import audio_processor

AUDIO_SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'audio_samples')
DUMMY_PCM_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm.wav')
DUMMY_OPUS_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_opus.opus')
DUMMY_PCM_RECOVERED_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm_recovered.wav')
DUMMY_PCM_STREAMING_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm_streaming.wav')


def test_opus_to_pcm() -> None:
    with open(DUMMY_OPUS_PATH, 'rb') as f:
        opus_data = f.read()
    pcm_data = audio_processor.opus_to_pcm(opus_data)
    assert isinstance(pcm_data, bytes)
    assert len(pcm_data) > 0


def test_pcm_to_opus() -> None:
    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    opus_data = audio_processor.pcm_to_opus(pcm_data)
    assert isinstance(opus_data, bytes)
    assert len(opus_data) > 0


def test_resample_audio() -> None:
    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    resampled = audio_processor.resample_audio(pcm_data, 8000, 16000)
    assert isinstance(resampled, bytes)
    assert len(resampled) > 0


def test_audio_stream_track() -> None:
    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    track = audio_processor.AudioStreamTrack(pcm_data, 16000)
    assert track.kind == 'audio'
    assert track.sample_rate == 16000
    assert hasattr(track, 'recv')


def test_pcm_to_opus_and_back() -> None:
    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    opus_data = audio_processor.pcm_to_opus(pcm_data)
    recovered_pcm = audio_processor.opus_to_pcm(opus_data)
    arr1 = np.frombuffer(pcm_data, dtype=np.int16)
    arr2 = np.frombuffer(recovered_pcm, dtype=np.int16)
    min_len = min(len(arr1), len(arr2))
    arr1 = arr1[:min_len]
    arr2 = arr2[:min_len]
    mse = np.mean((arr1 - arr2) ** 2)
    with open(DUMMY_PCM_RECOVERED_PATH, 'wb') as f:
        f.write(recovered_pcm)
    assert mse < 10000
