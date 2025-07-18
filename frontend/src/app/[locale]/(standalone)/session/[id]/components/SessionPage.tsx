'use client';

import { useEffect, useState } from 'react';
import { showErrorToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiClient';
import { ConnectionStatus, SessionStatus } from '@/interfaces/models/Session';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import SessionHeader from './SessionHeader';
import SessionMessages from './SessionMessages';
import SessionLiveFeedback from './SessionLiveFeedback';
import { useWebRTC } from '../hooks/useWebRTC';
import SessionFooter from './SessionFooter';

type SessionPageComponentProps = {
  personaName: string;
  categoryName: string;
  sessionId: string;
  ephemeralKey: string;
};

const DISCONNECTED_STATES = [
  ConnectionStatus.Connecting,
  ConnectionStatus.Disconnected,
  ConnectionStatus.Closed,
  ConnectionStatus.Failed,
];

const TERMINAL_STATES = [
  ConnectionStatus.Disconnected,
  ConnectionStatus.Closed,
  ConnectionStatus.Failed,
];

export default function SessionPageComponent({
  personaName,
  categoryName,
  sessionId,
  ephemeralKey,
}: SessionPageComponentProps) {
  const t = useTranslations('Session');
  const tCommon = useTranslations('Common');

  const router = useRouter();
  const [hangupInProgress, setHangupInProgress] = useState(false);

  const {
    isMicActive,
    connectionStatus,
    initWebRTC,
    remoteAudioRef,
    messages,
    elapsedTimeS,
    toggleMic,
    cleanup,
    sessionLiveFeedbacks,
  } = useWebRTC(sessionId, ephemeralKey);

  useEffect(() => {
    initWebRTC();
    return () => {
      cleanup();
    };
  }, [initWebRTC, cleanup]);

  const onDisconnect = async () => {
    try {
      setHangupInProgress(true);
      const { data } = await sessionService.updateSession(api, sessionId, {
        status: SessionStatus.COMPLETED,
      });
      cleanup();
      router.push(`/feedback/${data.id}`);
    } catch (err) {
      setHangupInProgress(false);
      showErrorToast(err, t('sessionEndError'));
    }
  };

  const isDisconnected = DISCONNECTED_STATES.includes(connectionStatus) || hangupInProgress;
  const isTerminalState = TERMINAL_STATES.includes(connectionStatus) && !hangupInProgress;
  const isConnecting = connectionStatus === ConnectionStatus.Connecting;
  const isConnected = connectionStatus === ConnectionStatus.Connected;

  return (
    <div className="flex flex-col h-screen">
      <div className="sticky top-0 z-11 bg-white">
        <SessionHeader
          characterName={personaName}
          sessionLabel={categoryName}
          time={elapsedTimeS}
          connectionStatus={connectionStatus}
        />
      </div>

      <div className="flex-1 relative p-4 overflow-y-auto mb-4 md:mb-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <SessionMessages messages={messages} />
        {isDisconnected && (
          <div className="absolute inset-0 backdrop-blur-sm bg-background z-10"></div>
        )}
      </div>

      <SessionLiveFeedback liveFeedbacks={sessionLiveFeedbacks} />

      <SessionFooter
        isMicActive={isMicActive}
        toggleMicrophone={toggleMic}
        isConnected={isConnected}
        onDisconnect={onDisconnect}
        isDisabled={hangupInProgress}
      />

      {isDisconnected && (
        <div className="fixed inset-0 flex flex-col items-center justify-center z-50 pointer-events-none">
          <Loader2 className="h-10 w-10 animate-spin text-marigold-50 mb-4" />
          <div className="text-center text-bw-70 font-medium">
            {hangupInProgress && <p>{t('hangingUp')}</p>}
            {isConnecting && <p>{t('connectingMessage')}</p>}
            {isTerminalState && <p>{t('disconnectedMessage')}</p>}
          </div>
        </div>
      )}

      <audio ref={remoteAudioRef} autoPlay playsInline />

      <div className="mt-4 mb-4 text-center">
        <p className="text-xs text-bw-40">{tCommon('aiDisclaimer')}</p>
      </div>
    </div>
  );
}
