import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiortc import RTCDataChannel, RTCPeerConnection
from fastapi import WebSocket

from ...schemas.webrtc_schema import (
    AudioControlConfig,
    WebRTCIceCandidate,
    WebRTCSignalingMessage,
    WebRTCSignalingType,
)
from ...services.webrtc_service import Peer, WebRTCService


@pytest.fixture
def websocket() -> WebSocket:
    """Create a mock WebSocket"""
    ws = MagicMock(spec=WebSocket)
    ws.client = 'test_client'
    return ws


@pytest.fixture
def peer_connection() -> RTCPeerConnection:
    """Create a mock RTCPeerConnection"""
    pc = MagicMock(spec=RTCPeerConnection)
    pc.createDataChannel = MagicMock()
    pc.setRemoteDescription = AsyncMock()
    pc.createAnswer = AsyncMock()
    pc.setLocalDescription = AsyncMock()
    pc.addIceCandidate = AsyncMock()
    pc.close = AsyncMock()
    return pc


@pytest.fixture
def data_channel() -> RTCDataChannel:
    """Create a mock RTCDataChannel"""
    channel = MagicMock(spec=RTCDataChannel)
    channel.close = MagicMock()
    return channel


@pytest.fixture
def webrtc_service() -> WebRTCService:
    """Create a WebRTCService instance"""
    return WebRTCService()


@pytest.mark.asyncio
async def test_handle_signaling_offer(
    webrtc_service: WebRTCService, websocket: WebSocket, peer_connection: RTCPeerConnection
) -> None:
    """Test handling offer message"""
    # Mock RTCPeerConnection creation
    with patch('backend.services.webrtc_service.RTCPeerConnection', return_value=peer_connection):
        # Create offer message
        offer_message = WebRTCSignalingMessage(
            type=WebRTCSignalingType.OFFER, sdp='test_sdp', audio_config=AudioControlConfig()
        )

        # Mock peer connection methods
        mock_answer = MagicMock(sdp='test_answer_sdp', type='answer')

        # Mock createAnswer to return our mock answer
        create_answer_mock = AsyncMock(return_value=mock_answer)
        peer_connection.createAnswer = create_answer_mock
        peer_connection.localDescription = mock_answer
        peer_connection.setRemoteDescription = AsyncMock()
        peer_connection.setLocalDescription = AsyncMock()

        # Create a task to set the channel ready event
        async def set_channel_ready() -> None:
            await asyncio.sleep(0.1)  # Small delay to ensure proper sequencing
            peer_id = str(id(websocket))
            if peer_id in webrtc_service.peers:
                webrtc_service.peers[peer_id].channel_ready.set()

        # Start the task
        asyncio.create_task(set_channel_ready())

        # Handle offer
        response = await webrtc_service.handle_signaling(offer_message, websocket)

        # Verify response
        assert response is not None
        assert response.type == WebRTCSignalingType.ANSWER
        assert response.sdp is not None
        assert response.audio_config is not None

        # Verify peer connection setup
        peer_connection.setRemoteDescription.assert_called_once()
        peer_connection.createAnswer.assert_called_once()
        peer_connection.setLocalDescription.assert_called_once()


@pytest.mark.asyncio
async def test_handle_signaling_candidate(
    webrtc_service: WebRTCService, websocket: WebSocket, peer_connection: RTCPeerConnection
) -> None:
    """Test handling ICE candidate message"""
    # Create peer
    peer_id = str(id(websocket))
    webrtc_service.peers[peer_id] = Peer(
        peer_id=peer_id, connection=peer_connection, channel_ready=asyncio.Event()
    )

    # Create candidate message
    candidate_message = WebRTCSignalingMessage(
        type=WebRTCSignalingType.CANDIDATE,
        candidate=WebRTCIceCandidate(
            type=WebRTCSignalingType.CANDIDATE,
            sdp_mid='test_sdp_mid',
            sdp_mline_index=0,
            candidate='test_candidate',
        ),
    )

    # Handle candidate
    response = await webrtc_service.handle_signaling(candidate_message, websocket)

    # Verify response
    assert response is not None
    assert response.type == WebRTCSignalingType.CANDIDATE
    assert response.candidate_response is not None
    assert response.candidate_response.status == 'success'
    assert 'ICE candidate added successfully' in response.candidate_response.message
    peer_connection.addIceCandidate.assert_called_once()


@pytest.mark.asyncio
async def test_setup_audio_channel(
    webrtc_service: WebRTCService,
    peer_connection: RTCPeerConnection,
    data_channel: RTCDataChannel,
) -> None:
    """Test setting up audio channel"""
    # Mock data channel creation
    peer_connection.createDataChannel.return_value = data_channel

    # Create peer
    peer_id = 'test_peer'
    peer = Peer(
        peer_id=peer_id,
        connection=peer_connection,
        channel_ready=asyncio.Event(),
        audio_config=AudioControlConfig(),
    )
    webrtc_service.peers[peer_id] = peer

    # Setup audio channel
    await webrtc_service.setup_audio_channel(peer_id)

    # Verify data channel creation
    peer_connection.createDataChannel.assert_called_once()
    assert peer.audio_channel == data_channel


@pytest.mark.asyncio
async def test_handle_audio_data(
    webrtc_service: WebRTCService,
    peer_connection: RTCPeerConnection,
) -> None:
    """Test handling audio data"""
    # Create peer
    peer_id = 'test_peer'
    peer = Peer(
        peer_id=peer_id,
        connection=peer_connection,
        channel_ready=asyncio.Event(),
        audio_config=AudioControlConfig(),
    )
    webrtc_service.peers[peer_id] = peer

    # Mock audio service
    webrtc_service.audio_service.write_audio_data = AsyncMock()

    # Handle audio data
    test_data = b'test_audio_data'
    await webrtc_service.handle_audio_data(test_data, peer_id)

    # Verify audio service call
    webrtc_service.audio_service.write_audio_data.assert_called_once_with(
        peer_id,
        test_data,
        sample_rate=peer.audio_config.sample_rate,
        buffer_size=peer.audio_config.buffer_size,
    )


@pytest.mark.asyncio
async def test_cleanup(
    webrtc_service: WebRTCService,
    websocket: WebSocket,
    peer_connection: RTCPeerConnection,
    data_channel: RTCDataChannel,
) -> None:
    """Test cleaning up peer connection"""
    # Create peer
    peer_id = str(id(websocket))
    peer = Peer(
        peer_id=peer_id,
        connection=peer_connection,
        audio_channel=data_channel,
        channel_ready=asyncio.Event(),
    )
    webrtc_service.peers[peer_id] = peer

    # Mock audio service
    webrtc_service.audio_service.cleanup = AsyncMock()

    # Cleanup
    await webrtc_service.cleanup(websocket)

    # Verify cleanup
    data_channel.close.assert_called_once()
    peer_connection.close.assert_called_once()
    webrtc_service.audio_service.cleanup.assert_called_once_with(peer_id)
    assert peer_id not in webrtc_service.peers


@pytest.mark.asyncio
async def test_handle_signaling_invalid_peer(
    webrtc_service: WebRTCService, websocket: WebSocket
) -> None:
    """Test handling signaling with invalid peer"""
    # Create candidate message
    candidate_message = WebRTCSignalingMessage(
        type=WebRTCSignalingType.CANDIDATE,
        candidate=WebRTCIceCandidate(
            type=WebRTCSignalingType.CANDIDATE,
            sdp_mid='test_sdp_mid',
            sdp_mline_index=0,
            candidate='test_candidate',
        ),
    )

    # Handle candidate
    response = await webrtc_service.handle_signaling(candidate_message, websocket)

    # Verify response
    assert response is not None
    assert response.type == WebRTCSignalingType.CANDIDATE
    assert response.candidate_response is not None
    assert response.candidate_response.status == 'error'
    assert 'No peer connection found' in response.candidate_response.message
    assert str(id(websocket)) not in webrtc_service.peers  # Peer should not be created


@pytest.mark.asyncio
async def test_handle_audio_data_invalid_peer(
    webrtc_service: WebRTCService,
) -> None:
    """Test handling audio data with invalid peer"""
    # Handle audio data
    test_data = b'test_audio_data'
    await webrtc_service.handle_audio_data(test_data, 'invalid_peer_id')

    # Verify no error occurred
    assert True
