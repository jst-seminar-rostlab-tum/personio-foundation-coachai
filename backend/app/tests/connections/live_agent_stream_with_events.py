#!/usr/bin/env python3
"""
Local audio stream event system demo

This script demonstrates how to use event handlers to monitor
various states and activities of audio streams.
"""

import asyncio
import logging

from app.tests.connections.live_agent_stream import (
    LocalAudioEvent,
    LocalAudioEventType,
    LocalDataChannelEvent,
    LocalDataChannelEventType,
    LocalSessionEvent,
    LocalSessionEventType,
    LocalWebRTCSimulator,
)

# Set logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventSystemDemo:
    """Event system demonstration class"""

    def __init__(self) -> None:
        self.simulator = LocalWebRTCSimulator()
        self.event_stats = {
            'audio_events': 0,
            'session_events': 0,
            'data_channel_events': 0,
        }

    async def custom_audio_event_handler(self, event: LocalAudioEvent) -> None:
        """Custom audio event handler"""
        self.event_stats['audio_events'] += 1

        if event.type == LocalAudioEventType.VOICE_ACTIVITY_DETECTED:
            print('Voice activity detected - Recording started!')
        elif event.type == LocalAudioEventType.SILENCE_DETECTED:
            print('Silence detected - Recording stopped.')
            if event.data and 'duration' in event.data:
                duration = event.data['duration']
                print(f'   Voice duration: {duration:.2f} seconds')
        elif event.type == LocalAudioEventType.AUDIO_STREAM_START:
            print('Audio stream started')
        elif event.type == LocalAudioEventType.AUDIO_STREAM_END:
            print('Audio stream ended')

        logger.debug(f'Audio events count: {self.event_stats["audio_events"]}')

    async def custom_session_event_handler(self, event: LocalSessionEvent) -> None:
        """Custom session event handler"""
        self.event_stats['session_events'] += 1

        if event.type == LocalSessionEventType.SESSION_STARTED:
            print('Local audio session started')
        elif event.type == LocalSessionEventType.GEMINI_CONNECTED:
            print('Connected to Gemini Live API')
        elif event.type == LocalSessionEventType.GEMINI_DISCONNECTED:
            print('Disconnected from Gemini')
        elif event.type == LocalSessionEventType.SESSION_ERROR:
            print(f'Session error: {event.data.get("error", "Unknown error")}')
        elif event.type == LocalSessionEventType.SESSION_ENDED:
            print('Local audio session ended')

        logger.debug(f'Session events count: {self.event_stats["session_events"]}')

    async def custom_data_channel_event_handler(self, event: LocalDataChannelEvent) -> None:
        """Custom data channel event handler"""
        self.event_stats['data_channel_events'] += 1

        if event.type == LocalDataChannelEventType.CHANNEL_READY:
            print('Data channel ready')
        elif event.type == LocalDataChannelEventType.TRANSCRIPT_SENT:
            transcript = event.data.get('transcript', '')
            print(f'Transcript sent: "{transcript[:50]}{"..." if len(transcript) > 50 else ""}"')
        elif event.type == LocalDataChannelEventType.MESSAGE_RECEIVED:
            print('Data channel message received')

        logger.debug(f'Data channel events count: {self.event_stats["data_channel_events"]}')

    def print_stats(self) -> None:
        """Print event statistics"""
        print('\n' + '=' * 50)
        print('Event Statistics:')
        print(f'   Audio events: {self.event_stats["audio_events"]}')
        print(f'   Session events: {self.event_stats["session_events"]}')
        print(f'   Data channel events: {self.event_stats["data_channel_events"]}')
        print('=' * 50 + '\n')

    async def run_demo(self) -> None:
        """Run the demonstration"""
        peer_id = 'demo_user'

        print('Starting event system demonstration...')
        print('=' * 50)

        try:
            # Create peer
            await self.simulator.create_peer(peer_id)

            # Get audio loop and add custom event handlers
            peer = self.simulator.get_peer(peer_id)
            if peer and peer.audio_loop:
                # Handlers should be added before start_audio_session
                # but due to architecture we need to handle this inside start_audio_session
                pass

            # Start audio session with our custom handlers
            await self._start_audio_session_with_custom_handlers(peer_id)

            print('\nVoice conversation started...')
            print('Tips:')
            print('   - Voice activity events will show when you speak')
            print('   - Silence events will show when you stop speaking')
            print('   - Transcript events will show when AI responds')
            print("   - Type 'q' to quit")
            print("   - Type 'stats' to view event statistics")

            # Wait for user input
            while True:
                try:
                    text = await asyncio.to_thread(input, '\nMessage > ')
                    if text.lower() == 'q':
                        break
                    elif text.lower() == 'stats':
                        self.print_stats()
                    else:
                        logger.info(f'User input: {text}')
                except KeyboardInterrupt:
                    break

        except Exception as e:
            logger.error(f'Demo error: {e}', exc_info=True)
        finally:
            # Clean up resources
            await self.simulator.close_peer(peer_id)
            self.print_stats()
            print('Demo finished')

    async def _start_audio_session_with_custom_handlers(self, peer_id: str) -> None:
        """Start audio session with custom event handlers"""
        peer = self.simulator.get_peer(peer_id)
        if not peer:
            raise ValueError(f'Peer {peer_id} does not exist')

        # Import LocalAudioLoop
        from app.tests.connections.live_agent_stream import LocalAudioLoop

        # Create audio loop
        audio_loop = LocalAudioLoop(peer_id)
        peer.audio_loop = audio_loop

        # Add default event handlers
        audio_loop.add_audio_event_handler(self.simulator._handle_audio_event)
        audio_loop.add_session_event_handler(self.simulator._handle_session_event)
        audio_loop.add_data_channel_event_handler(self.simulator._handle_data_channel_event)

        # Add our custom event handlers
        audio_loop.add_audio_event_handler(self.custom_audio_event_handler)
        audio_loop.add_session_event_handler(self.custom_session_event_handler)
        audio_loop.add_data_channel_event_handler(self.custom_data_channel_event_handler)

        # Set transcript callback
        audio_loop.set_transcript_callback(self.simulator._handle_transcript)

        # Mark data channel ready
        audio_loop.mark_data_channel_ready()

        # Start audio loop
        await audio_loop.start(peer)
        logger.info(f'Audio session with custom event handlers started for peer {peer_id}')


async def main() -> None:
    """Main function"""
    demo = EventSystemDemo()
    await demo.run_demo()


if __name__ == '__main__':
    asyncio.run(main())
