import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class AudioFile:
    """Audio file resource"""

    file_path: str
    file_handle: Optional[aiofiles.threadpool.AsyncBufferedIOBase] = None

    async def open(self) -> None:
        """Open audio file"""
        if not self.file_handle:
            self.file_handle = await aiofiles.open(self.file_path, 'wb')
            logger.info(f'Opened audio file: {self.file_path}')

    async def close(self) -> None:
        """Close audio file"""
        if self.file_handle:
            await self.file_handle.close()
            self.file_handle = None
            logger.info(f'Closed audio file: {self.file_path}')

    async def write(self, data: bytes) -> None:
        """Write audio data"""
        if self.file_handle:
            await self.file_handle.write(data)
            await self.file_handle.flush()
            logger.debug(f'Wrote {len(data)} bytes to {self.file_path}')


class AudioService:
    """Audio processing service"""

    def __init__(self, base_dir: str = 'audio_data') -> None:
        """Initialize audio service

        Args:
            base_dir: Base directory for audio file storage
        """
        self.base_dir = base_dir
        self.audio_files: dict[str, AudioFile] = {}
        os.makedirs(base_dir, exist_ok=True)

    async def create_audio_file(self, peer_id: str, sample_rate: int = 48000) -> str:
        """Create audio file for a specific peer

        Args:
            peer_id: Unique identifier for the peer
            sample_rate: Sample rate for the audio file
        Returns:
            str: Path to the audio file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.base_dir, f'audio_{peer_id}_{timestamp}.raw')

        audio_file = AudioFile(file_path=file_path)
        await audio_file.open()
        self.audio_files[peer_id] = audio_file

        logger.info(f'Created audio file for peer {peer_id}: {file_path}')
        return file_path

    async def write_audio_data(self, peer_id: str, data: bytes) -> None:
        """Write audio data

        Args:
            peer_id: Unique identifier for the peer
            data: Audio data
        """
        audio_file = self.audio_files.get(peer_id)
        if audio_file:
            try:
                if not audio_file.file_handle:
                    logger.warning(f'File handle is None for peer {peer_id}, reopening file')
                    await audio_file.open()

                await audio_file.write(data)
                logger.info(f'Wrote {len(data)} bytes to {audio_file.file_path}')
            except Exception as e:
                logger.error(f'Error writing audio data for peer {peer_id}: {e}')
                logger.exception(e)
        else:
            logger.error(f'No audio file found for peer {peer_id}')

    async def cleanup(self, peer_id: str) -> None:
        """Clean up audio resources for a specific peer

        Args:
            peer_id: Unique identifier for the peer
        """
        audio_file = self.audio_files.pop(peer_id, None)
        if audio_file:
            await audio_file.close()
            logger.info(f'Cleaned up audio resources for peer {peer_id}')

    async def cleanup_all(self) -> None:
        """Clean up all audio resources"""
        for peer_id in list(self.audio_files.keys()):
            await self.cleanup(peer_id)
