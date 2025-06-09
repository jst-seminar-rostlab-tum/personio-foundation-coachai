import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from aiortc import RTCDataChannel, RTCPeerConnection, RTCRtpTransceiver
from aiortc.mediastreams import MediaStreamTrack

from app.services.webrtc_service import (
    GeminiSessionManager,
    Peer,
    PeerManager,
    WebRTCAudioLoop,
    WebRTCService,
    get_webrtc_service,
)


class MockMediaStreamTrack(MediaStreamTrack):
    """Mock MediaStreamTrack for testing"""

    def __init__(self, kind: str = 'audio') -> None:
        super().__init__()
        self.kind = kind
        self._frames = []
        self._frame_index = 0

    def add_frame(self, frame: 'MockAudioFrame') -> None:
        """Add a mock audio frame"""
        self._frames.append(frame)

    async def recv(self) -> 'MockAudioFrame':
        """Simulate receiving an audio frame"""
        if self._frame_index < len(self._frames):
            frame = self._frames[self._frame_index]
            self._frame_index += 1
            return frame
        # If no more frames, wait a bit to avoid infinite loop
        await asyncio.sleep(0.1)
        raise StopAsyncIteration


class MockAudioFrame:
    """Mock audio frame"""

    def __init__(
        self,
        rate: int = 48000,
        sample_data: bytes = b'mock_audio_data',
    ) -> None:
        self.rate = rate
        self._sample_data = sample_data

    def to_ndarray(self) -> np.ndarray:
        """Return mock audio array"""
        return np.frombuffer(self._sample_data, dtype=np.int16)


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
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_transceiver() -> RTCRtpTransceiver:
    transceiver = MagicMock(spec=RTCRtpTransceiver)
    transceiver.stop = MagicMock()
    transceiver.sender = MagicMock()
    transceiver.sender.replaceTrack = MagicMock()
    return transceiver


@pytest.fixture
def service() -> WebRTCService:
    with patch('app.services.webrtc_service.get_client'):
        return WebRTCService()


@pytest.fixture
def peer_manager() -> PeerManager:
    return PeerManager()


@pytest.fixture
def audio_loop() -> WebRTCAudioLoop:
    return WebRTCAudioLoop('test_peer')


@pytest.fixture
def gemini_session_manager() -> GeminiSessionManager:
    with patch('app.services.webrtc_service.get_client'):
        return GeminiSessionManager()


# =============================================================================
# Peer class tests
# =============================================================================


class TestPeer:
    def test_peer_creation(
        self,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        """Test Peer object creation"""
        peer = Peer(
            peer_id='test_peer', connection=mock_peer_connection, transceiver=mock_transceiver
        )

        assert peer.peer_id == 'test_peer'
        assert peer.connection == mock_peer_connection
        assert peer.transceiver == mock_transceiver
        assert peer.data_channel is None

    @pytest.mark.asyncio
    async def test_peer_cleanup_closes_resources(
        self,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
        mock_data_channel: RTCDataChannel,
    ) -> None:
        """Test Peer cleanup functionality"""
        peer = Peer(
            peer_id='peer-4',
            connection=mock_peer_connection,
            transceiver=mock_transceiver,
            data_channel=mock_data_channel,
        )

        await peer.cleanup()

        mock_transceiver.stop.assert_called_once()
        mock_data_channel.close.assert_called_once()
        mock_peer_connection.close.assert_awaited_once()


# =============================================================================
# PeerManager class tests
# =============================================================================


class TestPeerManager:
    def test_callback_setting(self, peer_manager: PeerManager) -> None:
        """Test callback setting"""
        track_callback = AsyncMock()
        datachannel_callback = AsyncMock()

        peer_manager.set_track_callback(track_callback)
        peer_manager.set_datachannel_callback(datachannel_callback)

        assert peer_manager.on_track_callback == track_callback
        assert peer_manager.on_datachannel_callback == datachannel_callback

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.RTCPeerConnection')
    async def test_create_peer(
        self,
        mock_rtc_peer_connection: MagicMock,
        peer_manager: PeerManager,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        """Test creating a Peer"""
        mock_pc = AsyncMock(spec=RTCPeerConnection)
        mock_pc.addTransceiver.return_value = mock_transceiver
        mock_rtc_peer_connection.return_value = mock_pc

        peer = await peer_manager.create_peer('test_peer')

        assert peer.peer_id == 'test_peer'
        assert peer.connection == mock_pc
        assert peer.transceiver == mock_transceiver
        assert 'test_peer' in peer_manager.peers

    @pytest.mark.asyncio
    async def test_close_peer(self, peer_manager: PeerManager) -> None:
        """Test closing a Peer"""
        mock_peer = AsyncMock(spec=Peer)
        peer_manager.peers['test_peer'] = mock_peer

        await peer_manager.close_peer('test_peer')

        mock_peer.cleanup.assert_called_once()
        assert 'test_peer' not in peer_manager.peers

    def test_get_peer(self, peer_manager: PeerManager) -> None:
        """Test getting a Peer"""
        mock_peer = MagicMock(spec=Peer)
        peer_manager.peers['test_peer'] = mock_peer

        result = peer_manager.get_peer('test_peer')
        assert result == mock_peer

        result = peer_manager.get_peer('non_existent')
        assert result is None


# =============================================================================
# WebRTCAudioLoop class tests
# =============================================================================


class TestWebRTCAudioLoop:
    def test_audio_loop_creation(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test AudioLoop creation"""
        assert audio_loop.peer_id == 'test_peer'
        assert audio_loop.is_running is False
        assert audio_loop.audio_in_queue is None
        assert audio_loop.audio_out_queue is None

    def test_set_callbacks(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test setting callbacks"""
        transcript_callback = AsyncMock()
        send_callback = AsyncMock()

        audio_loop.set_transcript_callback(transcript_callback)
        audio_loop.set_send_to_gemini_callback(send_callback)

        assert audio_loop.on_transcript_callback == transcript_callback
        assert audio_loop._send_to_gemini_callback == send_callback

    @pytest.mark.asyncio
    async def test_start_and_stop(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test start and stop"""
        mock_track = MagicMock(spec=MediaStreamTrack)
        mock_peer = MagicMock(spec=Peer)

        # Test start
        await audio_loop.start(mock_track, mock_peer)

        assert audio_loop.is_running is True
        assert audio_loop.webrtc_track == mock_track
        assert audio_loop.peer == mock_peer
        assert audio_loop.audio_in_queue is not None
        assert audio_loop.audio_out_queue is not None
        assert len(audio_loop._tasks) == 3  # Three async tasks

        # Test stop
        await audio_loop.stop()

        assert audio_loop.is_running is False
        assert len(audio_loop._tasks) == 0

    @pytest.mark.asyncio
    async def test_receive_audio_from_gemini(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test receiving audio from Gemini"""
        await audio_loop.start(MagicMock(), MagicMock())

        test_audio_data = b'test_audio_data'
        await audio_loop.receive_audio_from_gemini(test_audio_data)

        # Verify audio data is put into the queue
        assert not audio_loop.audio_in_queue.empty()
        received_data = await audio_loop.audio_in_queue.get()
        assert received_data == test_audio_data

        await audio_loop.stop()

    @pytest.mark.asyncio
    async def test_handle_transcript(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test handling transcript"""
        callback = AsyncMock()
        audio_loop.set_transcript_callback(callback)

        await audio_loop.handle_transcript('test transcript')

        callback.assert_called_once_with('test transcript', 'test_peer')


# =============================================================================
# GeminiSessionManager class tests
# =============================================================================


class TestGeminiSessionManager:
    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.get_client')
    async def test_create_session(
        self, mock_get_client: MagicMock, gemini_session_manager: GeminiSessionManager
    ) -> None:
        """Test creating a session"""
        mock_client = MagicMock()
        mock_session = AsyncMock()
        mock_client.aio.live.connect.return_value.__aenter__.return_value = mock_session
        mock_get_client.return_value = mock_client

        gemini_session_manager.client = mock_client
        mock_audio_loop = MagicMock(spec=WebRTCAudioLoop)

        session = await gemini_session_manager.create_session('test_peer', mock_audio_loop)

        assert session == mock_session
        assert 'test_peer' in gemini_session_manager.sessions
        assert 'test_peer' in gemini_session_manager.audio_loops
        mock_audio_loop.set_send_to_gemini_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_session(self, gemini_session_manager: GeminiSessionManager) -> None:
        """Test closing a session"""
        mock_session = AsyncMock()
        # Use a real awaitable for the mock task
        import asyncio

        mock_task = asyncio.Future()
        mock_task.set_result(None)
        mock_audio_loop = MagicMock()

        # Set state
        gemini_session_manager.sessions['test_peer'] = mock_session
        gemini_session_manager.session_tasks['test_peer'] = [mock_task]
        gemini_session_manager.audio_loops['test_peer'] = mock_audio_loop

        await gemini_session_manager.close_session('test_peer')

        # No need to check cancel for Future, just check cleanup
        assert 'test_peer' not in gemini_session_manager.sessions
        assert 'test_peer' not in gemini_session_manager.session_tasks
        assert 'test_peer' not in gemini_session_manager.audio_loops


# =============================================================================
# WebRTCService class tests (original + new)
# =============================================================================


class TestWebRTCService:
    @pytest.mark.asyncio
    async def test_create_peer_connection_adds_peer(
        self,
        service: WebRTCService,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        """Test creating a peer connection adds a peer"""
        peer_id = 'peer-1'
        with patch(
            'app.services.webrtc_service.RTCPeerConnection', return_value=mock_peer_connection
        ):
            mock_peer_connection.addTransceiver.return_value = mock_transceiver
            await service.create_peer_connection(peer_id)
            assert peer_id in service.peer_manager.peers
            peer = service.peer_manager.peers[peer_id]
            assert isinstance(peer, Peer)
            assert peer.connection == mock_peer_connection

    @pytest.mark.asyncio
    async def test_create_peer_connection_replaces_existing_peer(
        self,
        service: WebRTCService,
        mock_peer_connection: RTCPeerConnection,
        mock_transceiver: RTCRtpTransceiver,
    ) -> None:
        """Test creating a peer connection replaces existing peer"""
        peer_id = 'peer-2'
        # Insert an old peer
        old_pc = MagicMock(spec=RTCPeerConnection)
        old_pc.close = AsyncMock()
        service.peer_manager.peers[peer_id] = Peer(peer_id=peer_id, connection=old_pc)
        with patch(
            'app.services.webrtc_service.RTCPeerConnection', return_value=mock_peer_connection
        ):
            mock_peer_connection.addTransceiver.return_value = mock_transceiver
            await service.create_peer_connection(peer_id)
            old_pc.close.assert_awaited_once()
            assert service.peer_manager.peers[peer_id].connection == mock_peer_connection

    @pytest.mark.asyncio
    async def test_close_peer_connection_removes_peer(
        self,
        service: WebRTCService,
        mock_peer_connection: RTCPeerConnection,
    ) -> None:
        """Test closing a peer connection removes the peer"""
        peer_id = 'peer-3'
        service.peer_manager.peers[peer_id] = Peer(peer_id=peer_id, connection=mock_peer_connection)
        mock_peer_connection.close = AsyncMock()

        await service.close_peer_connection(peer_id)

        mock_peer_connection.close.assert_awaited_once()
        assert peer_id not in service.peer_manager.peers

    @pytest.mark.asyncio
    async def test_handle_audio_track(self, service: WebRTCService) -> None:
        """Test handling audio track"""
        mock_track = MagicMock(spec=MediaStreamTrack)
        mock_track.kind = 'audio'

        mock_peer = MagicMock(spec=Peer)
        service.peer_manager.peers['test_peer'] = mock_peer

        with patch.object(service.gemini_manager, 'create_session') as mock_create_session:
            await service._handle_audio_track(mock_track, 'test_peer')

            # Verify audio loop is created
            assert hasattr(mock_peer, 'audio_loop')
            assert isinstance(mock_peer.audio_loop, WebRTCAudioLoop)

            # Verify Gemini session is created
            mock_create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_transcript(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        """Test handling transcript"""
        mock_peer = MagicMock(spec=Peer)
        mock_peer.data_channel = mock_data_channel
        service.peer_manager.peers['test_peer'] = mock_peer

        await service._handle_transcript('test transcript', 'test_peer')

        # Verify transcript is sent to data channel
        expected_message = json.dumps({'transcript': 'test transcript'})
        mock_data_channel.send.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_handle_data_channel(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        """Test handling data channel"""
        mock_peer = MagicMock(spec=Peer)
        service.peer_manager.peers['test_peer'] = mock_peer

        await service._handle_data_channel(mock_data_channel, 'test_peer')

        # Verify data channel is stored in peer
        assert mock_peer.data_channel == mock_data_channel


# =============================================================================
# Service singleton tests
# =============================================================================


class TestServiceSingleton:
    def test_get_webrtc_service_singleton(self) -> None:
        """Test getting WebRTC service singleton"""
        # Remove any existing instance
        if hasattr(get_webrtc_service, '_instance'):
            delattr(get_webrtc_service, '_instance')

        with patch('app.services.webrtc_service.get_client'):
            service1 = get_webrtc_service()
            service2 = get_webrtc_service()

            # Verify the same instance is returned
            assert service1 is service2
            assert isinstance(service1, WebRTCService)


# =============================================================================
# Integration tests
# =============================================================================


class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_audio_pipeline(self, service: WebRTCService) -> None:
        """Test full audio pipeline"""
        # Create mock objects
        mock_track = MockMediaStreamTrack()
        mock_frame = MockAudioFrame()
        mock_track.add_frame(mock_frame)

        # Create peer
        mock_peer = MagicMock(spec=Peer)
        mock_transceiver = MagicMock()
        mock_sender = MagicMock()
        mock_transceiver.sender = mock_sender
        mock_peer.transceiver = mock_transceiver
        mock_peer.data_channel = AsyncMock()

        service.peer_manager.peers['test_peer'] = mock_peer

        # Test audio track handling
        with patch.object(service.gemini_manager, 'create_session'):
            await service._handle_audio_track(mock_track, 'test_peer')

            # Verify audio loop is created and started
            assert hasattr(mock_peer, 'audio_loop')
            assert isinstance(mock_peer.audio_loop, WebRTCAudioLoop)
            assert mock_peer.audio_loop.is_running

            # Cleanup
            await service.close_peer_connection('test_peer')

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.resample_audio')
    @patch('app.services.webrtc_service.pcm_to_opus')
    async def test_audio_processing_pipeline(
        self,
        mock_pcm_to_opus: MagicMock,
        mock_resample_audio: MagicMock,
        audio_loop: WebRTCAudioLoop,
    ) -> None:
        """Test audio processing pipeline"""
        mock_pcm_to_opus.return_value = b'opus_data'
        mock_resample_audio.return_value = b'resampled_data'

        mock_track = MockMediaStreamTrack()
        mock_frame = MockAudioFrame(rate=44100)  # Test resampling with different sample rate
        mock_track.add_frame(mock_frame)

        mock_peer = MagicMock(spec=Peer)
        mock_transceiver = MagicMock()
        mock_peer.transceiver = mock_transceiver

        await audio_loop.start(mock_track, mock_peer)

        # Wait a short time for tasks to run
        await asyncio.sleep(0.1)

        # Verify audio processing
        assert not audio_loop.audio_out_queue.empty()

        await audio_loop.stop()
