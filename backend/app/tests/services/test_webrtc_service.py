from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiortc import RTCDataChannel, RTCPeerConnection

from app.services.webrtc_service import Peer, WebRTCService


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
    return channel


@pytest.fixture
def service() -> WebRTCService:
    return WebRTCService()


@pytest.mark.asyncio
async def test_create_peer_connection_adds_peer(
    service: WebRTCService,
    mock_peer_connection: RTCPeerConnection,
    mock_data_channel: RTCDataChannel,
) -> None:
    peer_id = 'peer-1'
    with patch('app.services.webrtc_service.RTCPeerConnection', return_value=mock_peer_connection):
        mock_peer_connection.addTransceiver.return_value = MagicMock()
        mock_peer_connection.createDataChannel.return_value = mock_data_channel
        await service.create_peer_connection(peer_id)
        assert peer_id in service.peers
        peer = service.peers[peer_id]
        assert isinstance(peer, Peer)
        assert peer.connection == mock_peer_connection
        assert peer.data_channel == mock_data_channel


@pytest.mark.asyncio
async def test_create_peer_connection_replaces_existing_peer(
    service: WebRTCService,
    mock_peer_connection: RTCPeerConnection,
    mock_data_channel: RTCDataChannel,
) -> None:
    peer_id = 'peer-2'
    # Insert an old peer
    old_pc = MagicMock(spec=RTCPeerConnection)
    old_pc.close = AsyncMock()
    service.peers[peer_id] = Peer(peer_id=peer_id, connection=old_pc)
    with patch('app.services.webrtc_service.RTCPeerConnection', return_value=mock_peer_connection):
        mock_peer_connection.addTransceiver.return_value = MagicMock()
        mock_peer_connection.createDataChannel.return_value = mock_data_channel
        await service.create_peer_connection(peer_id)
        old_pc.close.assert_awaited_once()
        assert service.peers[peer_id].connection == mock_peer_connection


@pytest.mark.asyncio
async def test_close_peer_connection_removes_peer(
    service: WebRTCService,
    mock_peer_connection: RTCPeerConnection,
    mock_data_channel: RTCDataChannel,
) -> None:
    peer_id = 'peer-3'
    service.peers[peer_id] = Peer(
        peer_id=peer_id, connection=mock_peer_connection, data_channel=mock_data_channel
    )
    mock_peer_connection.close = AsyncMock()
    await service.close_peer_connection(peer_id)
    mock_peer_connection.close.assert_awaited_once()
    assert peer_id not in service.peers


@pytest.mark.asyncio
async def test_peer_cleanup_closes_resources(
    mock_peer_connection: RTCPeerConnection,
    mock_data_channel: RTCDataChannel,
) -> None:
    peer = Peer(peer_id='peer-4', connection=mock_peer_connection, data_channel=mock_data_channel)
    await peer.cleanup()
    mock_data_channel.close.assert_called_once()
    mock_peer_connection.close.assert_awaited_once()
