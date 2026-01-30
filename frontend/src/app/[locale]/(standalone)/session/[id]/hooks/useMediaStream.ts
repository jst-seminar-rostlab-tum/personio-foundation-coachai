import { useRef, useState, useCallback } from 'react';

/**
 * Manages a local audio media stream and mic state.
 */
export function useMediaStream() {
  const localStreamRef = useRef<MediaStream | null>(null);
  const [isMicActive, setIsMicActive] = useState(false);

  /**
   * Requests microphone access and starts the audio stream.
   */
  const startStream = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      video: false,
    });
    localStreamRef.current = stream;
    setIsMicActive(true);
  }, []);

  /**
   * Stops all local audio tracks and clears state.
   */
  const stopStream = useCallback(() => {
    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    localStreamRef.current = null;
    setIsMicActive(false);
  }, []);

  /**
   * Toggles the enabled state of microphone tracks.
   */
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
