import logging
from dataclasses import dataclass

from aiortc import (
    RTCConfiguration,
    RTCDataChannel,
    RTCIceServer,
    RTCPeerConnection,
    RTCRtpTransceiver,
)
from aiortc.mediastreams import MediaStreamTrack

from app.schemas.webrtc_schema import (
    WebRTCConnectionError,
    WebRTCDataChannelError,
    WebRTCError,
    WebRTCIceError,
    WebRTCMediaError,
    WebRTCPeerError,
    WebRTCSignalingError,
)

logger = logging.getLogger(__name__)


RTC_CONFIG = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls=[
                'stun:stun.l.google.com:19302',
            ]
        ),
    ]
)


@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    transceiver: RTCRtpTransceiver | None = None
    data_channel: RTCDataChannel | None = None

    async def cleanup(self) -> None:
        """Cleanup all resources associated with this peer"""
        if self.transceiver:
            self.transceiver.stop()
        if self.data_channel:
            self.data_channel.close()
        await self.connection.close()


class WebRTCService:
    """WebRTC service for handling peer connections"""

    def __init__(self) -> None:
        """Initialize the WebRTC service"""
        self.peers: dict[str, Peer] = {}

    async def create_peer_connection(self, peer_id: str) -> None:
        """Create a new peer connection"""
        try:
            if peer_id in self.peers:
                logger.debug(f'Peer {peer_id} already exists, closing old connection')
                await self.peers[peer_id].connection.close()
                del self.peers[peer_id]

            # Create peer connection
            pc = RTCPeerConnection(RTC_CONFIG)

            # Add transceiver for audio
            try:
                transceiver = pc.addTransceiver('audio', direction='sendrecv')
                logger.debug(f'Created transceiver for peer {peer_id}')
            except Exception as e:
                raise WebRTCMediaError(
                    f'Failed to create audio transceiver: {str(e)}', peer_id
                ) from e

            # Register data channel handler for incoming channels
            try:
                data_channel = pc.createDataChannel(
                    'transcript', ordered=True, maxRetransmits=3, negotiated=False
                )
                logger.info(
                    f'[DataChannel] Created data channel on server side: {data_channel.label}'
                )
                logger.debug(f'[DataChannel] Initial state: {data_channel.readyState}')
            except Exception as e:
                raise WebRTCDataChannelError(
                    f'Failed to create data channel: {str(e)}', peer_id
                ) from e

            @pc.on('datachannel')
            async def on_datachannel(channel: RTCDataChannel) -> None:
                try:
                    logger.info(f'[DataChannel] Received data channel: {channel.label}')
                    logger.debug(f'[DataChannel] Channel state: {channel.readyState}')
                    logger.debug(f'[DataChannel] Channel protocol: {channel.protocol}')
                    logger.debug(f'[DataChannel] Channel negotiated: {channel.negotiated}')
                    logger.debug(f'[DataChannel] Channel id: {channel.id}')

                    if channel.label == 'transcript':
                        # TODO: send data channel to client
                        pass
                    logger.debug(f'[DataChannel] Stored received data channel for peer {peer_id}')
                except Exception as e:
                    raise WebRTCDataChannelError(
                        f'Error handling data channel: {str(e)}', peer_id
                    ) from e

            # Create peer object AFTER registering handlers
            self.peers[peer_id] = Peer(
                connection=pc, peer_id=peer_id, transceiver=transceiver, data_channel=data_channel
            )
            logger.info(f'Peer connection created for peer {peer_id}')

            @pc.on('track')
            async def on_track(track: MediaStreamTrack) -> None:
                try:
                    logger.info(f'Track {track.kind} received')
                    if track.kind == 'audio':
                        logger.info('Audio track received, sending back to client')
                        self.peers[peer_id].transceiver.sender.replaceTrack(track)
                        logger.debug('Audio track sent back to client')
                except Exception as e:
                    raise WebRTCMediaError(f'Error handling media track: {str(e)}', peer_id) from e

            @pc.on('connectionstatechange')
            async def on_connectionstatechange() -> None:
                try:
                    logger.debug(
                        f'[Connection] State changed to {pc.connectionState} for peer {peer_id}'
                    )
                    if pc.connectionState == 'connecting':
                        logger.debug(
                            f'[Connection] Peer {peer_id} connecting - establishing connection'
                        )
                    elif pc.connectionState == 'connected':
                        logger.info(f'[Connection] Peer {peer_id} connected successfully')
                        if (
                            self.peers[peer_id].data_channel
                            and self.peers[peer_id].data_channel.readyState == 'open'
                        ):
                            self.peers[peer_id].data_channel.send(
                                'test message from server after connection established'
                            )
                            logger.debug(
                                '[DataChannel] Test message sent after connection established'
                            )
                    elif pc.connectionState == 'failed':
                        raise WebRTCConnectionError(
                            f'Connection failed for peer {peer_id}', peer_id
                        )
                    elif pc.connectionState == 'disconnected':
                        logger.warning(f'[Connection] Peer {peer_id} connection disconnected')
                    elif pc.connectionState == 'closed':
                        logger.info(f'[Connection] Peer {peer_id} connection closed')
                    elif pc.connectionState == 'new':
                        logger.debug(f'[Connection] Peer {peer_id} connection new')
                except Exception as e:
                    if not isinstance(e, WebRTCError):
                        raise WebRTCConnectionError(
                            f'Error in connection state change: {str(e)}', peer_id
                        ) from e
                    raise

            @pc.on('iceconnectionstatechange')
            async def on_iceconnectionstatechange() -> None:
                try:
                    logger.debug(
                        f'[ICE] Connection state changed to {pc.iceConnectionState} '
                        f'for peer {peer_id}'
                    )
                    if pc.iceConnectionState == 'checking':
                        logger.debug(f'[ICE] Peer {peer_id} ICE checking - gathering candidates')
                    elif pc.iceConnectionState == 'connected':
                        logger.info(f'[ICE] Peer {peer_id} ICE connected successfully')
                        if (
                            self.peers[peer_id].data_channel
                            and self.peers[peer_id].data_channel.readyState == 'open'
                        ):
                            try:
                                self.peers[peer_id].data_channel.send(
                                    'test message from server after ICE connected'
                                )
                                logger.debug('[DataChannel] Test message sent after ICE connected')
                            except Exception as e:
                                raise WebRTCDataChannelError(
                                    f'Error sending test message: {str(e)}', peer_id
                                ) from e
                    elif pc.iceConnectionState == 'failed':
                        raise WebRTCIceError(f'ICE connection failed for peer {peer_id}', peer_id)
                    elif pc.iceConnectionState == 'disconnected':
                        logger.warning(f'[ICE] Peer {peer_id} ICE connection disconnected')
                    elif pc.iceConnectionState == 'closed':
                        logger.info(f'[ICE] Peer {peer_id} ICE connection closed')
                    elif pc.iceConnectionState == 'new':
                        logger.debug(f'[ICE] Peer {peer_id} ICE connection new')
                    elif pc.iceConnectionState == 'completed':
                        logger.debug(f'[ICE] Peer {peer_id} ICE connection completed')
                except Exception as e:
                    if not isinstance(e, WebRTCError):
                        raise WebRTCIceError(
                            f'Error in ICE connection state change: {str(e)}', peer_id
                        ) from e
                    raise

            @pc.on('icegatheringstatechange')
            async def on_icegatheringstatechange() -> None:
                try:
                    logger.debug(
                        f'[ICE] Gathering state changed to {pc.iceGatheringState} '
                        f'for peer {peer_id}'
                    )
                    if pc.iceGatheringState == 'gathering':
                        logger.debug(f'[ICE] Peer {peer_id} ICE gathering started')
                    elif pc.iceGatheringState == 'complete':
                        logger.debug(f'[ICE] Peer {peer_id} ICE gathering completed')
                    elif pc.iceGatheringState == 'new':
                        logger.debug(f'[ICE] Peer {peer_id} ICE gathering new')
                except Exception as e:
                    raise WebRTCIceError(
                        f'Error in ICE gathering state change: {str(e)}', peer_id
                    ) from e

            @pc.on('signalingstatechange')
            async def on_signalingstatechange() -> None:
                try:
                    logger.debug(
                        f'[Signaling] State changed to {pc.signalingState} for peer {peer_id}'
                    )
                    if pc.signalingState == 'stable':
                        logger.debug(f'[Signaling] Peer {peer_id} signaling stable')
                except Exception as e:
                    raise WebRTCSignalingError(
                        f'Error in signaling state change: {str(e)}', peer_id
                    ) from e

        except Exception as e:
            if not isinstance(e, WebRTCError):
                raise WebRTCPeerError(f'Error creating peer connection: {str(e)}', peer_id) from e
            raise

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        try:
            if peer_id in self.peers:
                await self.peers[peer_id].connection.close()
                del self.peers[peer_id]
                logger.info(f'Peer connection closed for peer {peer_id}')
        except Exception as e:
            raise WebRTCPeerError(f'Error closing peer connection: {str(e)}', peer_id) from e


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
