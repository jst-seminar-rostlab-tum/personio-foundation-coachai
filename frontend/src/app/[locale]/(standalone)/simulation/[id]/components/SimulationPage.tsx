'use client';

import { useEffect } from 'react';
import { useWebRTC } from '@/app/[locale]/(standalone)/simulation/[id]/hooks/useWebRTC';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';

export default function SimulationPageComponent({ sessionId }: { sessionId: string }) {
  const {
    isMicActive,
    setIsMicActive,
    isConnected,
    isDataChannelReady,
    initWebRTC,
    cleanup,
    disconnect,
    remoteAudioRef,
    localStreamRef,
    messages,
    elapsedTimeS,
    localAudioUrls,
    remoteAudioUrls,
  } = useWebRTC(sessionId);

  useEffect(() => {
    initWebRTC();
    return () => cleanup();
  }, [cleanup, initWebRTC]);

  const toggleMic = () => {
    localStreamRef.current?.getAudioTracks().forEach((track: MediaStreamTrack) => {
      // eslint-disable-next-line no-param-reassign
      track.enabled = !isMicActive;
    });
    setIsMicActive(!isMicActive);
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="mb-2">
        <SimulationHeader time={elapsedTimeS} />
      </div>

      <div className="flex-1 relative p-4 overflow-y-auto mb-4 md:mb-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SimulationMessages messages={messages} />
      </div>

      <SimulationRealtimeSuggestions />

      <SimulationFooter
        isMicActive={isMicActive}
        toggleMicrophone={toggleMic}
        isConnected={isConnected && isDataChannelReady}
        onDisconnect={disconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
      {localAudioUrls.map((url, idx) => (
        <a
          key={url}
          href={url}
          download={`recording-segment-${idx + 1}.wav`}
          className="block mt-2 text-blue-600 underline"
        >
          Download local segment {idx + 1}
        </a>
      ))}
      {remoteAudioUrls.map((url, idx) => (
        <a
          key={url}
          href={url}
          download={`recording-segment-${idx + 1}.wav`}
          className="block mt-2 text-blue-600 underline"
        >
          Download remote segment {idx + 1}
        </a>
      ))}
    </div>
  );
}
