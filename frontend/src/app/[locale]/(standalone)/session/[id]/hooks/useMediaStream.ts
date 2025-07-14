import { useRef, useState, useCallback } from 'react';

export function useMediaStream() {
  const localStreamRef = useRef<MediaStream | null>(null);
  const [isMicActive, setIsMicActive] = useState(false);

  const startStream = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      video: false,
    });
    localStreamRef.current = stream;
    setIsMicActive(true);
  }, []);

  const stopStream = useCallback(() => {
    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    localStreamRef.current = null;
    setIsMicActive(false);
  }, []);

  const toggleMic = useCallback(() => {
    const stream = localStreamRef.current;
    if (!stream) return;
    const audioTracks = stream.getAudioTracks();
    if (!audioTracks.length) return;
    const currentEnabled = audioTracks[0].enabled;
    audioTracks.forEach((track) => {
      // eslint-disable-next-line no-param-reassign
      track.enabled = !currentEnabled;
    });
    setIsMicActive(!currentEnabled);
  }, []);

  return { localStreamRef, startStream, stopStream, isMicActive, toggleMic };
}
