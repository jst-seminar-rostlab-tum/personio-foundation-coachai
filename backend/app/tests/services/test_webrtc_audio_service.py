import pytest

from app.services.webrtc_audio_service import WebRTCAudioLoop, webrtc_audio_service


def test_audio_loop_creation() -> None:
    loop = WebRTCAudioLoop('peer1')
    assert loop.peer_id == 'peer1'
    assert loop.audio_in_queue is None
    assert loop.audio_out_queue is None


@pytest.mark.asyncio
async def test_add_audio_data() -> None:
    loop = WebRTCAudioLoop('peer2')
    await loop.start()
    await loop.add_audio_data(b'abc')
    assert not loop.audio_in_queue.empty()
    await loop.stop()


def test_audio_service_create_and_get() -> None:
    loop = webrtc_audio_service.create_audio_loop('peer3')
    assert webrtc_audio_service.get_audio_loop('peer3') is loop
