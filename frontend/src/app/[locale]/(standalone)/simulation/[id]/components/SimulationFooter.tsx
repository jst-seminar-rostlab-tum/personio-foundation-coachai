'use client';

import { Pause, Play, Phone, Mic, MicOff } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

interface SimulationFooterProps {
  isPaused: boolean;
  setIsPaused: (isPaused: boolean) => void;
  isMicActive: boolean;
  toggleMicrophone: () => void;
  isConnected: boolean;
  onDisconnect: () => void;
  isSpeaking: boolean;
}

export default function SimulationFooter({
  isPaused,
  setIsPaused,
  isMicActive,
  toggleMicrophone,
  isConnected,
  onDisconnect,
  isSpeaking,
}: SimulationFooterProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-2 rounded-full ${
              isPaused ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            {isPaused ? '继续' : '暂停'}
          </button>
          <button
            onClick={toggleMicrophone}
            className={`p-2 rounded-full ${
              isMicActive ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            {isMicActive ? 'Mute' : 'Unmute'}
          </button>
          {isSpeaking && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-gray-600">Speaking...</span>
            </div>
          )}
        </div>
        <button
          onClick={onDisconnect}
          className={`p-2 rounded-full ${
            isConnected ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          Disconnect
        </button>
      </div>
    </div>
  );
}
