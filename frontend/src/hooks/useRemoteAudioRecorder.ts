import { useRef, useState } from 'react';

export function useRemoteAudioRecorder() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [remoteAudioUrls, setRemoteAudioUrls] = useState<string[]>([]);

  const startRemoteRecording = (stream: MediaStream): void => {
    if (mediaRecorderRef.current) return;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      const url = URL.createObjectURL(blob);
      setRemoteAudioUrls((prev) => [...prev, url]);
    };

    recorder.start();
  };

  const stopRemoteRecording = (): void => {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;
  };

  return {
    startRemoteRecording,
    stopRemoteRecording,
    remoteAudioUrls,
  };
}
