import asyncio

import pytest

from app.services.webrtc_event_manager import PeerEventManager, WebRTCEventManager
from app.services.webrtc_events import WebRTCAudioEvent, WebRTCAudioEventType


@pytest.mark.asyncio
async def test_audio_event_emit() -> None:
    manager = PeerEventManager('peer1')
    called = []

    @manager.on_audio_event(WebRTCAudioEventType.AUDIO_STREAM_START)
    async def handler(event: WebRTCAudioEvent) -> None:
        called.append(event.type)

    await manager.emit_audio_event(WebRTCAudioEventType.AUDIO_STREAM_START)
    await asyncio.sleep(0.1)
    assert called == [WebRTCAudioEventType.AUDIO_STREAM_START]


def test_get_or_create_peer_manager() -> None:
    event_manager = WebRTCEventManager()
    peer_mgr = event_manager.get_or_create_peer_manager('peerX')
    assert event_manager.get_peer_manager('peerX') is peer_mgr
