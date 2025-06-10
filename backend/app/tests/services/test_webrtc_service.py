import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from aiortc import RTCDataChannel, RTCPeerConnection, RTCRtpTransceiver
from aiortc.mediastreams import MediaStreamTrack
from google.genai import types

from app.schemas.webrtc_schema import WebRTCAudioEvent, WebRTCAudioEventType
from app.services.webrtc_service import (
    Peer,
    PeerSessionManager,
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
    """Mock audio frame with proper shape for testing"""

    def __init__(
        self,
        rate: int = 48000,
        channels: int = 1,
        samples: int = 320,  # 20ms at 16kHz
    ) -> None:
        self.rate = rate
        self.channels = channels
        self.samples = samples

    def to_ndarray(self) -> np.ndarray:
        """Return mock audio array with correct shape (channels, samples)"""
        if self.channels == 1:
            # Mono: shape (samples,) or (1, samples)
            return np.random.randint(-1000, 1000, size=self.samples, dtype=np.int16)
        else:
            # Multi-channel: shape (channels, samples)
            return np.random.randint(
                -1000, 1000, size=(self.channels, self.samples), dtype=np.int16
            )


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
    """Mock Gemini session"""
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
    """Mock Gemini client"""
    client = MagicMock()
    client.aio.live.connect.return_value = mock_gemini_session
    return client


@pytest.fixture
def service() -> WebRTCService:
    with patch('app.services.webrtc_service.get_client'):
        return WebRTCService()


@pytest.fixture
def peer_session_manager() -> PeerSessionManager:
    return PeerSessionManager()


@pytest.fixture
def audio_loop() -> WebRTCAudioLoop:
    with patch('app.services.webrtc_service.get_client'):
        return WebRTCAudioLoop('test_peer')


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
        """Test Peer cleanup functionality"""
        # Create mock audio loop
        mock_audio_loop = AsyncMock()
        mock_audio_loop.stop = AsyncMock()

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


# =============================================================================
# PeerSessionManager class tests
# =============================================================================


class TestPeerSessionManager:
    def test_callback_setting(self, peer_session_manager: PeerSessionManager) -> None:
        """Test callback setting"""
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
        """Test creating a Peer"""
        mock_pc = MagicMock(spec=RTCPeerConnection)
        # Mock the event decorator methods
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
        """Test closing a Peer"""
        mock_peer = AsyncMock(spec=Peer)
        peer_session_manager.peers['test_peer'] = mock_peer

        await peer_session_manager.close_peer('test_peer')

        mock_peer.cleanup.assert_awaited_once()
        assert 'test_peer' not in peer_session_manager.peers

    def test_get_peer(self, peer_session_manager: PeerSessionManager) -> None:
        """Test getting a Peer"""
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
        """Test PeerSessionManager duplicate create peer"""
        mock_pc = MagicMock(spec=RTCPeerConnection)
        # Mock the event decorator methods
        mock_pc.on = MagicMock(return_value=lambda func: func)
        mock_pc.addTransceiver.return_value = mock_transceiver
        mock_pc.close = AsyncMock()
        mock_rtc_peer_connection.return_value = mock_pc

        peer1 = await peer_session_manager.create_peer('dup_peer')
        peer2 = await peer_session_manager.create_peer('dup_peer')

        assert peer1 is not peer2
        assert peer_session_manager.peers['dup_peer'] == peer2


# =============================================================================
# WebRTCAudioLoop class tests
# =============================================================================


class TestWebRTCAudioLoop:
    def test_audio_loop_creation(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test AudioLoop creation"""
        assert audio_loop.peer_id == 'test_peer'
        assert audio_loop.audio_in_queue is None
        assert audio_loop.audio_out_queue is None
        assert audio_loop.gemini_session is None

    def test_set_transcript_callback(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test setting transcript callback"""
        transcript_callback = AsyncMock()
        audio_loop.set_transcript_callback(transcript_callback)
        assert audio_loop.on_transcript_callback == transcript_callback

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.get_client')
    async def test_start_initializes_queues_and_task(
        self, mock_get_client: MagicMock, audio_loop: WebRTCAudioLoop
    ) -> None:
        """Test start initializes queues and main task"""
        mock_track = MagicMock(spec=MediaStreamTrack)
        mock_peer = MagicMock(spec=Peer)
        mock_server_audio_track = MagicMock()

        # Mock the Gemini client and session
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_client.aio.live.connect.return_value = mock_session
        mock_get_client.return_value = mock_client

        await audio_loop.start(mock_track, mock_peer, mock_server_audio_track)

        assert audio_loop.webrtc_track == mock_track
        assert audio_loop.peer == mock_peer
        assert audio_loop.server_audio_track == mock_server_audio_track
        assert audio_loop._main_task is not None
        assert not audio_loop._main_task.done()

        await audio_loop.stop()

    @pytest.mark.asyncio
    async def test_stop_cancels_task_and_clears_queues(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test stop cancels main task and clears queues"""
        # Initialize queues
        audio_loop.audio_in_queue = asyncio.Queue()
        audio_loop.audio_in_queue.put_nowait(types.Blob(data=b'test', mime_type='audio/pcm'))

        # Create a real asyncio task that we can cancel
        async def dummy_task() -> None:
            await asyncio.sleep(10)  # Long running task

        task = asyncio.create_task(dummy_task())
        audio_loop._main_task = task

        await audio_loop.stop()

        assert task.cancelled()
        assert audio_loop.audio_in_queue.empty()

    @pytest.mark.asyncio
    async def test_handle_transcript_calls_callback(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test handle_transcript calls callback if data channel is ready"""
        callback = AsyncMock()
        audio_loop.set_transcript_callback(callback)

        # Mark data channel as ready
        audio_loop.mark_data_channel_ready()

        await audio_loop.handle_transcript('test transcript')

        callback.assert_awaited_once_with('test transcript', 'test_peer')

    @pytest.mark.asyncio
    async def test_handle_transcript_queues_when_not_ready(
        self, audio_loop: WebRTCAudioLoop
    ) -> None:
        """Test handle_transcript queues transcript when data channel is not ready"""
        callback = AsyncMock()
        audio_loop.set_transcript_callback(callback)

        # Don't mark data channel as ready
        await audio_loop.handle_transcript('test transcript')

        # Callback should not be called
        callback.assert_not_awaited()

        # Transcript should be queued
        assert 'test transcript' in audio_loop._pending_transcripts

    @pytest.mark.asyncio
    async def test_handle_transcript_no_callback(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test handle_transcript when no callback is set"""
        # Mark data channel as ready
        audio_loop.mark_data_channel_ready()

        # Should not raise an exception
        await audio_loop.handle_transcript('test transcript')

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.is_silence', return_value=False)
    @patch('app.services.webrtc_service.resample_pcm_audio')
    async def test_listen_webrtc_audio_processes_frames(
        self, mock_resample: MagicMock, mock_is_silence: MagicMock, audio_loop: WebRTCAudioLoop
    ) -> None:
        """Test _listen_webrtc_audio processes audio frames correctly"""
        # Setup
        mock_frame = MockAudioFrame(rate=48000, channels=1, samples=320)
        mock_track = MagicMock()
        mock_track.recv = AsyncMock(side_effect=[mock_frame, asyncio.CancelledError()])

        audio_loop.webrtc_track = mock_track
        audio_loop.audio_out_queue = asyncio.Queue()
        audio_loop.last_voice_time = asyncio.get_event_loop().time()

        # Mock resample function
        mock_resample.return_value = b'x' * 400  # 长度大于320

        # Run the method until cancelled
        with pytest.raises(asyncio.CancelledError):
            await audio_loop._listen_webrtc_audio()

        # Verify resampling was called
        mock_resample.assert_called()
        # Verify audio was queued
        assert not audio_loop.audio_out_queue.empty()

    @pytest.mark.asyncio
    async def test_send_to_gemini_audio_blob(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test _send_to_gemini with audio blob"""
        mock_session = AsyncMock()
        audio_loop.gemini_session = mock_session

        audio_blob = types.Blob(data=b'audio_data', mime_type='audio/pcm')
        await audio_loop._send_to_gemini(audio_blob)

        mock_session.send_realtime_input.assert_awaited_once_with(audio=audio_blob)

    @pytest.mark.asyncio
    async def test_send_to_gemini_content(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test _send_to_gemini with content"""
        mock_session = AsyncMock()
        audio_loop.gemini_session = mock_session

        content = types.Content(role='user', parts=[types.Part(text='Hello')])
        await audio_loop._send_to_gemini(content)

        mock_session.send_client_content.assert_awaited_once_with(turns=[content])

    @pytest.mark.asyncio
    async def test_send_to_gemini_audio_event(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test _send_to_gemini with audio event"""
        mock_session = AsyncMock()
        audio_loop.gemini_session = mock_session

        event = WebRTCAudioEvent(type=WebRTCAudioEventType.AUDIO_STREAM_END)
        await audio_loop._send_to_gemini(event)

        # Should not call any send methods for AUDIO_STREAM_END
        mock_session.send_realtime_input.assert_not_called()
        mock_session.send_client_content.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_to_gemini_no_session(self, audio_loop: WebRTCAudioLoop) -> None:
        """Test _send_to_gemini when no session is available"""
        audio_loop.gemini_session = None

        audio_blob = types.Blob(data=b'audio_data', mime_type='audio/pcm')
        # Should not raise an exception
        await audio_loop._send_to_gemini(audio_blob)


# =============================================================================
# WebRTCService class tests
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
            # Mock the event decorator methods
            mock_peer_connection.on = MagicMock(return_value=lambda func: func)
            mock_peer_connection.addTransceiver.return_value = mock_transceiver
            await service.create_peer_connection(peer_id)

            assert peer_id in service.peer_session_manager.peers
            peer = service.peer_session_manager.peers[peer_id]
            assert isinstance(peer, Peer)
            assert peer.connection == mock_peer_connection

    @pytest.mark.asyncio
    async def test_close_peer_connection_removes_peer(self, service: WebRTCService) -> None:
        """Test closing a peer connection removes the peer"""
        peer_id = 'peer-3'
        mock_peer = AsyncMock(spec=Peer)
        service.peer_session_manager.peers[peer_id] = mock_peer

        await service.close_peer_connection(peer_id)

        mock_peer.cleanup.assert_awaited_once()
        assert peer_id not in service.peer_session_manager.peers

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.AudioStreamTrack')
    @patch('app.services.webrtc_service.WebRTCAudioLoop')
    async def test_handle_audio_track(
        self,
        mock_audio_loop_class: MagicMock,
        mock_audio_stream_track_class: MagicMock,
        service: WebRTCService,
    ) -> None:
        """Test handling audio track"""
        # Setup mocks
        mock_track = MagicMock(spec=MediaStreamTrack)
        mock_track.kind = 'audio'

        mock_peer = MagicMock(spec=Peer)
        mock_transceiver = MagicMock()
        mock_sender = MagicMock()
        mock_transceiver.sender = mock_sender
        mock_peer.transceiver = mock_transceiver

        service.peer_session_manager.peers['test_peer'] = mock_peer

        mock_audio_loop = AsyncMock()
        mock_audio_loop.set_transcript_callback = MagicMock()
        mock_audio_loop.start = AsyncMock()
        mock_audio_loop_class.return_value = mock_audio_loop

        mock_server_audio_track = MagicMock()
        mock_audio_stream_track_class.return_value = mock_server_audio_track

        # Call the method
        await service._handle_audio_track(mock_track, 'test_peer')

        # Verify audio loop was created and configured
        mock_audio_loop_class.assert_called_once_with('test_peer')
        mock_audio_loop.set_transcript_callback.assert_called_once()
        mock_audio_loop.start.assert_awaited_once_with(
            mock_track, mock_peer, mock_server_audio_track
        )

        # Verify track was replaced
        mock_sender.replaceTrack.assert_called_once_with(mock_server_audio_track)

        # Verify peer's audio_loop was set
        assert mock_peer.audio_loop == mock_audio_loop

    @pytest.mark.asyncio
    async def test_handle_transcript_sends_to_data_channel(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        """Test handling transcript sends to data channel"""
        mock_peer = MagicMock(spec=Peer)
        mock_peer.data_channel = mock_data_channel
        service.peer_session_manager.peers['test_peer'] = mock_peer

        await service._handle_transcript('test transcript', 'test_peer')

        expected_message = json.dumps({'transcript': 'test transcript'})
        mock_data_channel.send.assert_called_once_with(expected_message)

    @pytest.mark.asyncio
    async def test_handle_transcript_peer_not_found(self, service: WebRTCService) -> None:
        """Test _handle_transcript when peer is not found"""
        # Should not raise an exception
        await service._handle_transcript('hello', 'non_existent_peer')

    @pytest.mark.asyncio
    async def test_handle_transcript_data_channel_closed(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        """Test _handle_transcript when data channel is closed"""
        mock_data_channel.readyState = 'closed'
        mock_peer = MagicMock(spec=Peer)
        mock_peer.data_channel = mock_data_channel
        service.peer_session_manager.peers['test_peer'] = mock_peer

        await service._handle_transcript('hello', 'test_peer')

        mock_data_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_data_channel(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        """Test handling data channel"""
        mock_peer = MagicMock(spec=Peer)
        service.peer_session_manager.peers['test_peer'] = mock_peer

        await service._handle_data_channel(mock_data_channel, 'test_peer')

        assert mock_peer.data_channel == mock_data_channel

    @pytest.mark.asyncio
    async def test_handle_data_channel_peer_not_found(
        self, service: WebRTCService, mock_data_channel: RTCDataChannel
    ) -> None:
        """Test _handle_data_channel when peer is not found"""
        # Should not raise an exception
        await service._handle_data_channel(mock_data_channel, 'non_existent_peer')


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
    @patch('app.services.webrtc_service.AudioStreamTrack')
    @patch('app.services.webrtc_service.WebRTCAudioLoop')
    async def test_full_audio_pipeline(
        self,
        mock_audio_loop_class: MagicMock,
        mock_audio_stream_track_class: MagicMock,
        service: WebRTCService,
    ) -> None:
        """Test full audio pipeline from track to Gemini"""
        # Create mock objects
        mock_track = MockMediaStreamTrack()
        mock_frame = MockAudioFrame(rate=48000, channels=1, samples=320)
        mock_track.add_frame(mock_frame)

        # Create peer with proper setup
        peer_id = 'test_peer'
        with patch('app.services.webrtc_service.RTCPeerConnection') as mock_pc_class:
            # Create a proper mock that handles event decorators
            mock_pc = MagicMock()
            # Mock the event decorator methods
            mock_pc.on = MagicMock(
                return_value=lambda func: func
            )  # Return decorator that does nothing
            mock_pc.addTransceiver = MagicMock()
            mock_pc.close = AsyncMock()

            mock_transceiver = MagicMock()
            mock_sender = MagicMock()
            mock_transceiver.sender = mock_sender
            mock_pc.addTransceiver.return_value = mock_transceiver
            mock_pc_class.return_value = mock_pc

            await service.create_peer_connection(peer_id)

        # Setup audio loop mock
        mock_audio_loop = AsyncMock()
        mock_audio_loop.set_transcript_callback = MagicMock()
        mock_audio_loop.start = AsyncMock()
        mock_audio_loop_class.return_value = mock_audio_loop

        mock_server_audio_track = MagicMock()
        mock_audio_stream_track_class.return_value = mock_server_audio_track

        # Test audio track handling
        await service._handle_audio_track(mock_track, peer_id)

        # Verify the pipeline was set up correctly
        mock_audio_loop_class.assert_called_once_with(peer_id)
        mock_audio_loop.set_transcript_callback.assert_called_once()
        mock_audio_loop.start.assert_awaited_once()

        # Verify peer has audio loop
        peer = service.peer_session_manager.get_peer(peer_id)
        assert peer.audio_loop == mock_audio_loop

        # Cleanup
        await service.close_peer_connection(peer_id)

    @pytest.mark.asyncio
    @patch('app.services.webrtc_service.resample_pcm_audio')
    async def test_audio_resampling_integration(
        self, mock_resample: MagicMock, audio_loop: WebRTCAudioLoop
    ) -> None:
        """Test audio resampling integration"""
        mock_resample.return_value = b'resampled_audio_data'

        # Setup frame with different sample rate
        mock_frame = MockAudioFrame(rate=44100, channels=1, samples=441)  # 10ms at 44.1kHz
        mock_track = MagicMock()
        mock_track.recv = AsyncMock(side_effect=[mock_frame, asyncio.CancelledError()])

        audio_loop.webrtc_track = mock_track
        audio_loop.audio_out_queue = asyncio.Queue()
        audio_loop.last_voice_time = asyncio.get_event_loop().time()

        # Run the audio processing
        with pytest.raises(asyncio.CancelledError):
            await audio_loop._listen_webrtc_audio()

        # Verify resampling was called with correct parameters
        mock_resample.assert_called()
        call_args = mock_resample.call_args
        assert len(call_args[0]) >= 2  # audio_bytes, source_rate, target_rate

        # Verify audio was queued
        assert not audio_loop.audio_out_queue.empty()
        queued_item = await audio_loop.audio_out_queue.get()
        assert isinstance(queued_item, types.Blob)
        assert queued_item.mime_type == 'audio/pcm'
        assert queued_item.data == b'resampled_audio_data'
