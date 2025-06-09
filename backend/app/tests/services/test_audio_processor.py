import os
import wave

import numpy as np

from app.services import audio_processor

AUDIO_SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'audio_samples')
DUMMY_PCM_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm.wav')
DUMMY_OPUS_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_opus.opus')
DUMMY_PCM_RECOVERED_PATH = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm_recovered.wav')
DUMMY_PCM_RECOVERED_PATH_2 = os.path.join(AUDIO_SAMPLE_DIR, 'dummy_pcm_recovered_2.wav')


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


def test_resample_wav_audio() -> None:
    with open(DUMMY_PCM_PATH, 'rb') as f:
        pcm_data = f.read()
    resampled = audio_processor.resample_wav_audio(pcm_data, 8000, 16000)
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


def test_resample_pcm_audio() -> None:
    with wave.open(DUMMY_PCM_PATH, 'rb') as wf:
        pcm_data = wf.readframes(wf.getnframes())
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
    assert sample_width == 2
    target_rate = sample_rate * 2 if sample_rate < 32000 else sample_rate // 2
    resampled = audio_processor.resample_pcm_audio(
        pcm_data, sample_rate, target_rate, channels=n_channels
    )
    assert isinstance(resampled, bytes)
    assert len(resampled) > 0
    ratio = len(resampled) / len(pcm_data)
    expected_ratio = target_rate / sample_rate
    assert abs(ratio - expected_ratio) < 0.2
    with wave.open(DUMMY_PCM_RECOVERED_PATH_2, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(target_rate)
        wf.writeframes(resampled)
