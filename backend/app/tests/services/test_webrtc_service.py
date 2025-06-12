import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiortc import RTCDataChannel, RTCPeerConnection, RTCRtpTransceiver

from app.schemas.webrtc_schema import WebRTCDataChannelMessage
from app.services.webrtc_service import (
    Peer,
    PeerSessionManager,
    WebRTCService,
)


class TestPeer:
    def test_peer_creation(
        self,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        peer = Peer(
            peer_id='test_peer',
            connection=mock_peer_connection,
            transceiver=mock_transceiver,
        )
        assert peer.peer_id == 'test_peer'
        assert peer.connection == mock_peer_connection
        assert peer.transceiver == mock_transceiver
        assert peer.data_channel is None
        assert peer.audio_loop is None

    @pytest.mark.asyncio
    async def test_peer_cleanup_closes_resources(
        self,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
        mock_data_channel: RTCDataChannel,
    ) -> None:
        mock_audio_loop = AsyncMock()
        mock_audio_loop.stop = AsyncMock()
        mock_audio_loop.event_manager = MagicMock()
        peer = Peer(
            peer_id='peer-4',
            connection=mock_peer_connection,
            transceiver=mock_transceiver,
            data_channel=mock_data_channel,
            audio_loop=mock_audio_loop,
        )
        await peer.cleanup()
        mock_audio_loop.stop.assert_awaited_once()
        mock_transceiver.stop.assert_called_once()
        mock_data_channel.close.assert_called_once()
        mock_peer_connection.close.assert_awaited_once()


class TestPeerSessionManager:
    def test_callback_setting(self, peer_session_manager: PeerSessionManager) -> None:
        track_callback = AsyncMock()
        datachannel_callback = AsyncMock()
        peer_session_manager.set_track_callback(track_callback)
        peer_session_manager.set_datachannel_callback(datachannel_callback)
        assert peer_session_manager.on_track_callback == track_callback
        assert peer_session_manager.on_datachannel_callback == datachannel_callback

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.RTCPeerConnection')
    async def test_create_peer(
        self,
        mock_rtc_peer_connection: MagicMock,
        peer_session_manager: PeerSessionManager,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        mock_pc = MagicMock(spec=RTCPeerConnection)
        mock_pc.on = MagicMock(return_value=lambda func: func)
        mock_pc.addTransceiver.return_value = mock_transceiver
        mock_pc.close = AsyncMock()
        mock_rtc_peer_connection.return_value = mock_pc
        peer = await peer_session_manager.create_peer('test_peer')
        assert peer.peer_id == 'test_peer'
        assert peer.connection == mock_pc
        assert peer.transceiver == mock_transceiver
        assert 'test_peer' in peer_session_manager.peers

    @pytest.mark.asyncio
    async def test_close_peer(self, peer_session_manager: PeerSessionManager) -> None:
        mock_peer = AsyncMock(spec=Peer)
        peer_session_manager.peers['test_peer'] = mock_peer
        await peer_session_manager.close_peer('test_peer')
        mock_peer.cleanup.assert_awaited_once()
        assert 'test_peer' not in peer_session_manager.peers

    def test_get_peer(self, peer_session_manager: PeerSessionManager) -> None:
        mock_peer = MagicMock(spec=Peer)
        peer_session_manager.peers['test_peer'] = mock_peer
        result = peer_session_manager.get_peer('test_peer')
        assert result == mock_peer
        result = peer_session_manager.get_peer('non_existent')
        assert result is None

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.RTCPeerConnection')
    async def test_create_peer_duplicate(
        self,
        mock_rtc_peer_connection: MagicMock,
        peer_session_manager: PeerSessionManager,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        mock_pc = MagicMock(spec=RTCPeerConnection)
        mock_pc.on = MagicMock(return_value=lambda func: func)
        mock_pc.addTransceiver.return_value = mock_transceiver
        mock_pc.close = AsyncMock()
        mock_rtc_peer_connection.return_value = mock_pc
        peer1 = await peer_session_manager.create_peer('dup_peer')
        peer2 = await peer_session_manager.create_peer('dup_peer')
        assert peer1 is not peer2
        assert peer_session_manager.peers['dup_peer'] == peer2


class TestWebRTCService:
    @pytest.mark.asyncio
    async def test_create_peer_connection_adds_peer(
        self,
        service: WebRTCService,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        peer_id = 'peer-1'
        with patch(
            'app.services.webrtc_service.RTCPeerConnection', return_value=mock_peer_connection
        ):
            mock_peer_connection.on = MagicMock(return_value=lambda func: func)
            mock_peer_connection.addTransceiver.return_value = mock_transceiver
            await service.create_peer_connection(peer_id)
            assert peer_id in service.peer_session_manager.peers
            peer = service.peer_session_manager.peers[peer_id]
            assert isinstance(peer, Peer)
            assert peer.connection == mock_peer_connection

    @pytest.mark.asyncio
    async def test_close_peer_connection_removes_peer(self, service: WebRTCService) -> None:
        peer_id = 'peer-3'
        mock_peer = AsyncMock(spec=Peer)
        service.peer_session_manager.peers[peer_id] = mock_peer
        await service.close_peer_connection(peer_id)
        mock_peer.cleanup.assert_awaited_once()
        assert peer_id not in service.peer_session_manager.peers

    @pytest.mark.asyncio
    async def test_handle_transcript_sends_to_data_channel(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        mock_peer = MagicMock(spec=Peer)
        mock_peer.data_channel = mock_data_channel
        service.peer_session_manager.peers['test_peer'] = mock_peer
        await service._handle_transcript(
            WebRTCDataChannelMessage(role='user', text='test transcript'), 'test_peer'
        )
        expected_message = json.dumps(
            {
                'transcript': WebRTCDataChannelMessage(
                    role='user', text='test transcript'
                ).model_dump()
            }
        )
        mock_data_channel.send.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_handle_transcript_peer_not_found(self, service: WebRTCService) -> None:
        await service._handle_transcript(
            WebRTCDataChannelMessage(role='user', text='hello'), 'non_existent_peer'
        )

    @pytest.mark.asyncio
    async def test_handle_transcript_data_channel_closed(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        mock_data_channel.readyState = 'closed'
        mock_peer = MagicMock(spec=Peer)
        mock_peer.data_channel = mock_data_channel
        service.peer_session_manager.peers['test_peer'] = mock_peer
        await service._handle_transcript(
            WebRTCDataChannelMessage(role='user', text='hello'), 'test_peer'
        )
        mock_data_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_data_channel(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        mock_peer = MagicMock(spec=Peer)
        service.peer_session_manager.peers['test_peer'] = mock_peer
        await service._handle_data_channel(mock_data_channel, 'test_peer')
        assert mock_peer.data_channel == mock_data_channel

    @pytest.mark.asyncio
    async def test_handle_data_channel_peer_not_found(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        await service._handle_data_channel(mock_data_channel, 'non_existent_peer')
