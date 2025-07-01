import { useRef, useState, useCallback } from 'react';

export function useRemoteAudioRecorder() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [remoteAudioUrls, setRemoteAudioUrls] = useState<string[]>([]);

  const startRemoteRecording = useCallback((stream: MediaStream) => {
    if (mediaRecorderRef.current) return;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.start();
  }, []);

  const stopRemoteRecording = useCallback((): Promise<Blob> => {
    return new Promise((resolve) => {
      const recorder = mediaRecorderRef.current;
      if (!recorder) {
        resolve(new Blob());
        return;
      }

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setRemoteAudioUrls((prev) => [...prev, url]);
        resolve(blob);
        mediaRecorderRef.current = null;
      };

      recorder.stop();
    });
  }, []);

  return {
    startRemoteRecording,
    stopRemoteRecording,
    remoteAudioUrls,
  };
}
