# def test_audio_loop_creation() -> None:
#     loop = WebRTCAudioLoop('peer1')
#     assert loop.peer_id == 'peer1'
#     assert loop.audio_in_queue is None
#     assert loop.audio_out_queue is None


# @pytest.mark.asyncio
# async def test_add_audio_data() -> None:
#     loop = WebRTCAudioLoop('peer2')
#     await loop.start()
#     await loop.add_audio_data(b'abc')
#     assert not loop.audio_in_queue.empty()
#     await loop.stop()


# def test_audio_service_create_and_get() -> None:
#     loop = webrtc_audio_service.create_audio_loop('peer3')
#     assert webrtc_audio_service.get_audio_loop('peer3') is loop


# @pytest.mark.asyncio
# @patch('app.services.webrtc_audio_service.resample_pcm_audio')
# async def test_audio_resampling_integration(
#     mock_resample_webrtc: MagicMock,
#     audio_loop: WebRTCAudioLoop,
# ) -> None:
#     mock_resample_webrtc.return_value = b'x' * 400
#     mock_frame = MockAudioFrame(rate=44100, channels=1, samples=441)
#     mock_track = MagicMock()
#     mock_track.recv = AsyncMock(side_effect=[mock_frame, asyncio.CancelledError()])
#     audio_loop.webrtc_track = mock_track
#     audio_loop.audio_out_queue = asyncio.Queue()
#     audio_loop.last_voice_time = asyncio.get_event_loop().time()
#     audio_loop.segmenter = MagicMock()
#     audio_loop.segmenter.feed = MagicMock(return_value=[b'x' * 400])
#     with pytest.raises(asyncio.CancelledError):
#         await audio_loop._listen_webrtc_audio()
#     mock_resample_webrtc.assert_called()
#     call_args = mock_resample_webrtc.call_args
#     assert len(call_args[0]) >= 2
#     assert not audio_loop.audio_out_queue.empty()
#     queued_item = await audio_loop.audio_out_queue.get()
#     assert isinstance(queued_item, types.Blob)
#     assert queued_item.mime_type == 'audio/pcm'
#     assert queued_item.data == b'x' * 400
