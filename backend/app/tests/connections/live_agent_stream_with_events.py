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
    LocalAudioLoop,
    LocalDataChannelEvent,
    LocalDataChannelEventType,
    LocalSessionEvent,
    LocalSessionEventType,
    LocalUserEvent,
    LocalUserEventType,
    LocalWebRTCSimulator,
)

# Set logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventSystemDemo(LocalWebRTCSimulator):
    """Event system demonstration class (inherits from LocalWebRTCSimulator)"""

    def __init__(self) -> None:
        super().__init__()
        self.event_stats = {
            'audio_events': 0,
            'session_events': 0,
            'data_channel_events': 0,
        }

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
            await self.create_peer(peer_id)

            # Start audio session with our custom handlers
            await self.start_audio_session(peer_id)

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
                        peer = self.get_peer(peer_id)
                        audio_loop = peer.audio_loop if peer else None
                        event_manager = audio_loop.event_manager if audio_loop else None
                        if event_manager:
                            await event_manager.emit_user_event(
                                LocalUserEventType.USER_MESSAGE_SENT, {'message': text}
                            )
                except KeyboardInterrupt:
                    break

        except Exception as e:
            logger.error(f'Demo error: {e}', exc_info=True)
        finally:
            # Clean up resources
            await self.close_peer(peer_id)
            self.print_stats()
            print('Demo finished')

    async def start_audio_session(self, peer_id: str) -> None:
        """Start audio session with event handlers (decorator style)"""
        peer = self.get_peer(peer_id)
        if not peer:
            raise ValueError(f'Peer {peer_id} does not exist')

        audio_loop = LocalAudioLoop(peer_id)
        peer.audio_loop = audio_loop
        event_manager = audio_loop.event_manager

        # Register custom event handlers using event_manager decorators
        @event_manager.on_audio_event(LocalAudioEventType.VOICE_ACTIVITY_DETECTED)
        async def on_voice(event: LocalAudioEvent[str]) -> None:
            self.event_stats['audio_events'] += 1
            print('Voice activity detected - Recording started!')

        @event_manager.on_audio_event(LocalAudioEventType.SILENCE_DETECTED)
        async def on_silence(event: LocalAudioEvent[str]) -> None:
            self.event_stats['audio_events'] += 1
            print('Silence detected - Recording stopped.')
            if event.data and 'duration' in event.data:
                duration = event.data['duration']
                print(f'   Voice duration: {duration:.2f} seconds')

        @event_manager.on_audio_event(LocalAudioEventType.AUDIO_STREAM_START)
        async def on_audio_start(event: LocalAudioEvent[str]) -> None:
            self.event_stats['audio_events'] += 1
            print('Audio stream started')

        @event_manager.on_audio_event(LocalAudioEventType.AUDIO_STREAM_END)
        async def on_audio_end(event: LocalAudioEvent[str]) -> None:
            self.event_stats['audio_events'] += 1
            print('Audio stream ended')

        @event_manager.on_session_event(LocalSessionEventType.SESSION_STARTED)
        async def on_session_started(event: LocalSessionEvent[str]) -> None:
            self.event_stats['session_events'] += 1
            print('Local audio session started')

        @event_manager.on_session_event(LocalSessionEventType.GEMINI_CONNECTED)
        async def on_gemini_connected(event: LocalSessionEvent[str]) -> None:
            self.event_stats['session_events'] += 1
            print('Connected to Gemini Live API')

        @event_manager.on_session_event(LocalSessionEventType.GEMINI_DISCONNECTED)
        async def on_gemini_disconnected(event: LocalSessionEvent[str]) -> None:
            self.event_stats['session_events'] += 1
            print('Disconnected from Gemini')

        @event_manager.on_session_event(LocalSessionEventType.SESSION_ERROR)
        async def on_session_error(event: LocalSessionEvent[str]) -> None:
            self.event_stats['session_events'] += 1
            print(f'Session error: {event.data.get("error", "Unknown error")}')

        @event_manager.on_session_event(LocalSessionEventType.SESSION_ENDED)
        async def on_session_ended(event: LocalSessionEvent[str]) -> None:
            self.event_stats['session_events'] += 1
            print('Local audio session ended')

        @event_manager.on_data_channel_event(LocalDataChannelEventType.CHANNEL_READY)
        async def on_channel_ready(event: LocalDataChannelEvent[str]) -> None:
            self.event_stats['data_channel_events'] += 1
            print('Data channel ready')

        @event_manager.on_data_channel_event(LocalDataChannelEventType.TRANSCRIPT_SENT)
        async def on_transcript_sent(event: LocalDataChannelEvent[str]) -> None:
            self.event_stats['data_channel_events'] += 1
            transcript = event.data.get('transcript', '')
            print(f'Transcript sent: "{transcript[:50]}{"..." if len(transcript) > 50 else ""}"')

        @event_manager.on_data_channel_event(LocalDataChannelEventType.MESSAGE_RECEIVED)
        async def on_message_received(event: LocalDataChannelEvent[str]) -> None:
            self.event_stats['data_channel_events'] += 1
            print('Data channel message received')

        @event_manager.on_user_event(LocalUserEventType.USER_MESSAGE_SENT)
        async def on_user_message(event: LocalUserEvent[str]) -> None:
            msg = event.data['message'] if event.data else None
            if msg:
                await audio_loop._send_to_gemini(msg)
                print(f'[UserMessage] Sent to Gemini: {msg}')

        # Register default event handlers from parent class
        await super().start_audio_session(peer_id)


async def main() -> None:
    """Main function"""
    demo = EventSystemDemo()
    await demo.run_demo()


if __name__ == '__main__':
    asyncio.run(main())
