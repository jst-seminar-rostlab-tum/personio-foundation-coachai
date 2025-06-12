from unittest.mock import AsyncMock, MagicMock

import pytest
from aiortc import RTCDataChannel, RTCPeerConnection, RTCRtpTransceiver

from app.services.webrtc_audio_service import WebRTCAudioLoop
from app.services.webrtc_event_manager import PeerEventManager
from app.services.webrtc_service import PeerSessionManager, WebRTCService


@pytest.fixture
def mock_peer_connection() -> RTCPeerConnection:
    pc = MagicMock(spec=RTCPeerConnection)
    pc.addTransceiver = MagicMock()
    pc.createDataChannel = MagicMock()
    pc.close = AsyncMock()
    return pc


@pytest.fixture
def mock_data_channel() -> RTCDataChannel:
    channel = MagicMock(spec=RTCDataChannel)
    channel.close = MagicMock()
    channel.readyState = 'open'
    channel.label = 'transcript'
    channel.send = MagicMock()
    return channel


@pytest.fixture
def mock_transceiver() -> RTCRtpTransceiver:
    transceiver = MagicMock(spec=RTCRtpTransceiver)
    transceiver.stop = MagicMock()
    transceiver.sender = MagicMock()
    transceiver.sender.replaceTrack = MagicMock()
    return transceiver


@pytest.fixture
def mock_gemini_session() -> MagicMock:
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.send_realtime_input = AsyncMock()
    session.send_client_content = AsyncMock()
    session.send = AsyncMock()
    session.receive = MagicMock()
    return session


@pytest.fixture
def mock_gemini_client(mock_gemini_session: MagicMock) -> MagicMock:
    client = MagicMock()
    client.aio.live.connect.return_value = mock_gemini_session
    return client


@pytest.fixture
def service() -> WebRTCService:
    return WebRTCService()


@pytest.fixture
def peer_session_manager() -> PeerSessionManager:
    return PeerSessionManager()


@pytest.fixture
def audio_loop() -> WebRTCAudioLoop:
    return WebRTCAudioLoop('test_peer')


@pytest.fixture
def mock_event_manager() -> PeerEventManager:
    event_manager = MagicMock(spec=PeerEventManager)
    event_manager.emit_data_channel_event = AsyncMock()
    event_manager.emit_audio_event = AsyncMock()
    event_manager.emit_session_event = AsyncMock()
    event_manager.emit_user_event = AsyncMock()
    return event_manager
