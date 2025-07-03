'use client';

import { useEffect } from 'react';
import { useWebRTC } from '@/app/[locale]/(standalone)/simulation/[id]/hooks/useWebRTC';
import { showErrorToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiClient';
import { SessionStatus } from '@/interfaces/models/Session';
import { useRouter } from 'next/navigation';
import SimulationHeader from './SimulationHeader';
import SimulationFooter from './SimulationFooter';
import SimulationRealtimeSuggestions from './SimulationRealtimeSuggestions';
import SimulationMessages from './SimulationMessages';

export default function SimulationPageComponent({ sessionId }: { sessionId: string }) {
  const t = useTranslations('Simulation');
  const router = useRouter();
  const {
    isMicActive,
    isConnected,
    initWebRTC,
    remoteAudioRef,
    messages,
    elapsedTimeS,
    audioUrls,
    toggleMic,
    cleanup,
  } = useWebRTC(sessionId);

  useEffect(() => {
    initWebRTC();
    return () => {
      cleanup();
    };
  }, [initWebRTC, sessionId, cleanup]);

  const onDisconnect = async () => {
    try {
      cleanup();
      const { data } = await sessionService.updateSession(api, sessionId, {
        status: SessionStatus.COMPLETED,
      });
      router.push(`/feedback/${data.id}`);
    } catch (err) {
      showErrorToast(err, t('sessionEndError'));
    }
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
        isConnected={isConnected}
        onDisconnect={onDisconnect}
      />
      <audio ref={remoteAudioRef} autoPlay playsInline />
      {audioUrls.map(({ url, filename }) => (
        <a
          key={url}
          href={url}
          download={`${filename}.wav`}
          className="block mt-2 text-blue-600 underline"
        >
          {filename}
        </a>
      ))}
    </div>
  );
}
