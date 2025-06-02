import logging
from dataclasses import dataclass
from typing import Optional

from aiortc import (
    RTCPeerConnection,
    RTCRtpTransceiver,
    RTCDataChannel,
    RTCConfiguration,
    RTCIceServer,
)
from aiortc.mediastreams import MediaStreamTrack
from fastapi import WebSocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


RTC_CONFIG = RTCConfiguration(
    iceServers=[
        RTCIceServer(
            urls=['stun:stun.l.google.com:19302']
        ),
    ]
)

@dataclass
class Peer:
    """Peer connection and its associated resources"""

    peer_id: str
    connection: RTCPeerConnection
    transceiver: Optional[RTCRtpTransceiver] = None
    data_channel: Optional[RTCDataChannel] = None

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

    async def create_peer_connection(self, websocket: WebSocket, peer_id: str) -> None:
        """Create a new peer connection"""
        if peer_id in self.peers:
            logger.info(f'Peer {peer_id} already exists, closing old connection')
            await self.peers[peer_id].connection.close()
            del self.peers[peer_id]

        # Create peer connection
        pc = RTCPeerConnection(RTC_CONFIG)
        
        # Add transceiver for audio
        transceiver = pc.addTransceiver('audio', direction='sendrecv')
        logger.info(f'Created transceiver for peer {peer_id}')

        self.peers[peer_id] = Peer(connection=pc, peer_id=peer_id, transceiver=transceiver)

        @pc.on('datachannel')
        async def on_datachannel(channel: RTCDataChannel) -> None:
            logger.info(f'[DataChannel] Received data channel: {channel.label}')
            logger.info(f'[DataChannel] Channel state: {channel.readyState}')
            logger.info(f'[DataChannel] Channel protocol: {channel.protocol}')
            logger.info(f'[DataChannel] Channel negotiated: {channel.negotiated}')
            logger.info(f'[DataChannel] Channel id: {channel.id}')
            
            self.peers[peer_id].data_channel = channel
            logger.info(f'[DataChannel] Stored data channel for peer {peer_id}')

            @channel.on('open')
            async def on_open() -> None:
                logger.info(f'[DataChannel] Channel {channel.label} opened for peer {peer_id}')
                logger.info(f'[DataChannel] Channel state after open: {channel.readyState}')
                try:
                    # Send a test message back to client
                    channel.send('test message from server')
                    logger.info('[DataChannel] Test message sent to client')
                except Exception as e:
                    logger.error(f'[DataChannel] Error sending test message: {e}')

            @channel.on('message')
            async def on_message(message: str) -> None:
                logger.info(f'[DataChannel] Received message from peer {peer_id}: {message}')
                logger.info(f'[DataChannel] Channel state during message: {channel.readyState}')
                try:
                    # Echo the message back to client
                    channel.send(f'Echo: {message}')
                    logger.info(f'[DataChannel] Echo message sent to client: {message}')
                except Exception as e:
                    logger.error(f'[DataChannel] Error sending echo message: {e}')

            @channel.on('close')
            async def on_close() -> None:
                logger.info(f'[DataChannel] Channel {channel.label} closed for peer {peer_id}')
                logger.info(f'[DataChannel] Channel state after close: {channel.readyState}')
                if peer_id in self.peers:
                    self.peers[peer_id].data_channel = None
                    logger.info(f'[DataChannel] Cleared data channel reference for peer {peer_id}')

            @channel.on('error')
            async def on_error(error: Exception) -> None:
                logger.error(f'[DataChannel] Channel {channel.label} error for peer {peer_id}: {error}')
                logger.error(f'[DataChannel] Channel state during error: {channel.readyState}')

        @pc.on('track')
        async def on_track(track: MediaStreamTrack) -> None:
            logger.info(f'Track {track.kind} received')
            if track.kind == 'audio':
                logger.info('Audio track received, sending back to client')

                # TODO: send audio to LLM
                self.peers[peer_id].transceiver.sender.replaceTrack(track)
                logger.info('Audio track sent back to client')

        @pc.on('connectionstatechange')
        async def on_connectionstatechange() -> None:
            logger.info(f'[Connection] State changed to {pc.connectionState} for peer {peer_id}')
            if pc.connectionState == 'connecting':
                logger.info(f'[Connection] Peer {peer_id} connecting - establishing connection')
            elif pc.connectionState == 'connected':
                logger.info(f'[Connection] Peer {peer_id} connected successfully')
                # Try to send a test message through data channel if it exists
                if self.peers[peer_id].data_channel and self.peers[peer_id].data_channel.readyState == 'open':
                    try:
                        self.peers[peer_id].data_channel.send('test message from server after connection established')
                        logger.info('[DataChannel] Test message sent after connection established')
                    except Exception as e:
                        logger.error(f'[DataChannel] Error sending test message after connection established: {e}')
            elif pc.connectionState == 'failed':
                logger.error(f'[Connection] Peer {peer_id} connection failed')
                await pc.close()
                if peer_id in self.peers:
                    del self.peers[peer_id]
            elif pc.connectionState == 'disconnected':
                logger.warning(f'[Connection] Peer {peer_id} connection disconnected')
            elif pc.connectionState == 'closed':
                logger.info(f'[Connection] Peer {peer_id} connection closed')
            elif pc.connectionState == 'new':
                logger.info(f'[Connection] Peer {peer_id} connection new')

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange() -> None:
            logger.info(f'[ICE] Connection state changed to {pc.iceConnectionState} for peer {peer_id}')
            if pc.iceConnectionState == 'checking':
                logger.info(f'[ICE] Peer {peer_id} ICE checking - gathering candidates')
            elif pc.iceConnectionState == 'connected':
                logger.info(f'[ICE] Peer {peer_id} ICE connected successfully')
                # Try to send a test message through data channel if it exists
                if self.peers[peer_id].data_channel and self.peers[peer_id].data_channel.readyState == 'open':
                    try:
                        self.peers[peer_id].data_channel.send('test message from server after ICE connected')
                        logger.info('[DataChannel] Test message sent after ICE connected')
                    except Exception as e:
                        logger.error(f'[DataChannel] Error sending test message after ICE connected: {e}')
            elif pc.iceConnectionState == 'failed':
                logger.error(f'[ICE] Peer {peer_id} ICE connection failed')
                await pc.close()
                if peer_id in self.peers:
                    del self.peers[peer_id]
            elif pc.iceConnectionState == 'disconnected':
                logger.warning(f'[ICE] Peer {peer_id} ICE connection disconnected')
            elif pc.iceConnectionState == 'closed':
                logger.info(f'[ICE] Peer {peer_id} ICE connection closed')
            elif pc.iceConnectionState == 'new':
                logger.info(f'[ICE] Peer {peer_id} ICE connection new')
            elif pc.iceConnectionState == 'completed':
                logger.info(f'[ICE] Peer {peer_id} ICE connection completed')

        @pc.on('icegatheringstatechange')
        async def on_icegatheringstatechange() -> None:
            logger.info(f'[ICE] Gathering state changed to {pc.iceGatheringState} for peer {peer_id}')
            if pc.iceGatheringState == 'gathering':
                logger.info(f'[ICE] Peer {peer_id} ICE gathering started')
            elif pc.iceGatheringState == 'complete':
                logger.info(f'[ICE] Peer {peer_id} ICE gathering completed')
            elif pc.iceGatheringState == 'new':
                logger.info(f'[ICE] Peer {peer_id} ICE gathering new')

        @pc.on('signalingstatechange')
        async def on_signalingstatechange() -> None:
            logger.info(f'[Signaling] State changed to {pc.signalingState} for peer {peer_id}')
            if pc.signalingState == 'stable':
                logger.info(f'[Signaling] Peer {peer_id} signaling stable')

        logger.info(f'Peer connection created for peer {peer_id}')

    async def close_peer_connection(self, peer_id: str) -> None:
        """Close a peer connection"""
        if peer_id in self.peers:
            await self.peers[peer_id].connection.close()
            del self.peers[peer_id]
            logger.info(f'Peer connection closed for peer {peer_id}')


def get_webrtc_service() -> WebRTCService:
    """
    Get WebRTC service instance

    Returns:
        WebRTCService: Global instance of WebRTC service
    """
    if not hasattr(get_webrtc_service, '_instance'):
        get_webrtc_service._instance = WebRTCService()
    return get_webrtc_service._instance
