import { useRef } from 'react';

export function useMediaStream() {
  const localStreamRef = useRef<MediaStream | null>(null);

  const startStream = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      video: false,
    });
    localStreamRef.current = stream;
    return stream;
  };

  const stopStream = () => {
    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    localStreamRef.current = null;
  };

  return { localStreamRef, startStream, stopStream };
}
