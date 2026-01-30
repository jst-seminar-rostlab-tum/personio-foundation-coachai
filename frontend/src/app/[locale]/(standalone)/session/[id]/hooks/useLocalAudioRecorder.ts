/* eslint-disable no-param-reassign */
import { useRef, useCallback } from 'react';

/**
 * Tracks a MediaRecorder instance and its buffered chunks.
 */
type LocalAudioRecorder = {
  recorder: MediaRecorder;
  chunks: Blob[];
  startOffsetMs: number;
};

const INACTIVITY_TIMEOUT_MS = 300000;
const AUDIO_MIME_TYPE = 'audio/webm';

/**
 * Converts an AudioBuffer into a WAV Blob.
 */
const bufferToWav = async (buffer: AudioBuffer): Promise<Blob> => {
  const numOfChan = buffer.numberOfChannels;
  const length = buffer.length * numOfChan * 2 + 44;
  const bufferArray = new ArrayBuffer(length);
  const view = new DataView(bufferArray);

  let pos = 0;

  const setUint16 = (data: number): void => {
    view.setUint16(pos, data, true);
    pos += 2;
  };

  const setUint32 = (data: number): void => {
    view.setUint32(pos, data, true);
    pos += 4;
  };

  setUint32(0x46464952); // "RIFF"
  setUint32(length - 8);
  setUint32(0x45564157); // "WAVE"
  setUint32(0x20746d66); // "fmt "
  setUint32(16);
  setUint16(1);
  setUint16(numOfChan);
  setUint32(buffer.sampleRate);
  setUint32(buffer.sampleRate * numOfChan * 2);
  setUint16(numOfChan * 2);
  setUint16(16);
  setUint32(0x61746164); // "data"
  setUint32(length - pos - 4);

  const channels: Float32Array[] = [];
  for (let i = 0; i < numOfChan; i += 1) {
    channels.push(buffer.getChannelData(i));
  }

  let offset = 0;
  while (offset < buffer.length) {
    for (let i = 0; i < numOfChan; i += 1) {
      const sample = Math.max(-1, Math.min(1, channels[i][offset]));
      view.setInt16(pos, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      pos += 2;
    }
    offset += 1;
  }

  return new Blob([bufferArray], { type: 'audio/wav' });
};

/**
 * Manages local audio recording and extracts WAV segments by time offsets.
 */
export function useLocalAudioRecorder(localStreamRef: React.RefObject<MediaStream | null>) {
  const currentIndexRef = useRef(0);
  const recorderARef = useRef<LocalAudioRecorder | null>(null);
  const recorderBRef = useRef<LocalAudioRecorder | null>(null);
  const inactivityTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Memoized helpers
  /**
   * Returns the currently active recorder ref.
   */
  const getCurrentRecorderRef = useCallback(
    () => (currentIndexRef.current === 0 ? recorderARef : recorderBRef),
    []
  );

  /**
   * Stops a recorder and clears its chunks.
   */
  const stopAndResetRecorder = useCallback(
    (recorderRef: React.RefObject<LocalAudioRecorder | null>) => {
      if (recorderRef.current) {
        recorderRef.current.recorder.stop();
        recorderRef.current.chunks = [];
        recorderRef.current = null;
      }
    },
    []
  );

  /**
   * Creates and starts a recorder with a start offset.
   */
  const initializeRecorder = useCallback(
    (recorderRef: React.RefObject<LocalAudioRecorder | null>, startOffsetMs: number) => {
      if (recorderRef.current) {
        recorderRef.current.recorder.stop();
      }
      if (!localStreamRef.current) return;

      const newRecorder: LocalAudioRecorder = {
        recorder: new MediaRecorder(localStreamRef.current, { mimeType: AUDIO_MIME_TYPE }),
        chunks: [],
        startOffsetMs,
      };

      newRecorder.recorder.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) newRecorder.chunks.push(e.data);
      };

      newRecorder.recorder.start();
      recorderRef.current = newRecorder;
    },
    [localStreamRef]
  );

  /**
   * Starts dual local recording buffers.
   */
  const startLocalRecording = useCallback((): void => {
    if (recorderARef.current && recorderBRef.current) return; // Already running
    initializeRecorder(recorderARef, 0);
    initializeRecorder(recorderBRef, 0);
    currentIndexRef.current = 0;
  }, [initializeRecorder]);

  /**
   * Stops local recording and clears timers.
   */
  const stopLocalRecording = useCallback((): void => {
    stopAndResetRecorder(recorderARef);
    stopAndResetRecorder(recorderBRef);
    localStreamRef.current = null;
    if (inactivityTimeoutRef.current) {
      clearTimeout(inactivityTimeoutRef.current);
      inactivityTimeoutRef.current = null;
    }
  }, [stopAndResetRecorder, localStreamRef]);

  /**
   * Stops a recorder and resolves its recorded chunks.
   */
  const stopRecorderAndCollectChunks = useCallback(
    (recorderRef: React.RefObject<LocalAudioRecorder | null>): Promise<Blob[]> => {
      return new Promise((resolve) => {
        if (!recorderRef.current) {
          resolve([]);
          return;
        }
        const { chunks, recorder } = recorderRef.current;
        const onStop = () => {
          recorder.removeEventListener('stop', onStop);
          resolve([...chunks]);
        };
        recorder.addEventListener('stop', onStop);
        recorder.stop();
      });
    },
    []
  );

  /**
   * Resets the inactivity timeout that restarts recorders.
   */
  const resetInactivityTimeout = useCallback(
    (elapsedTimeMs: number) => {
      if (inactivityTimeoutRef.current) {
        clearTimeout(inactivityTimeoutRef.current);
      }
      inactivityTimeoutRef.current = setTimeout(() => {
        if (recorderARef.current && recorderBRef.current) {
          initializeRecorder(recorderARef, elapsedTimeMs + INACTIVITY_TIMEOUT_MS);
          initializeRecorder(recorderBRef, elapsedTimeMs + INACTIVITY_TIMEOUT_MS);
        }
      }, INACTIVITY_TIMEOUT_MS);
    },
    [initializeRecorder]
  );

  /**
   * Extracts a WAV segment between offsets from the active recorder.
   */
  const extractSegment = useCallback(
    async (startOffsetMs: number, endOffsetMs: number, elapsedTimeMs: number): Promise<Blob> => {
      const currentRef = getCurrentRecorderRef();
      if (!currentRef.current) return new Blob();

      resetInactivityTimeout(elapsedTimeMs);

      const t0 = performance.now();
      const chunks = await stopRecorderAndCollectChunks(currentRef);
      const t1 = performance.now();

      const currentMediaRecorderStartOffsetMs = currentRef.current.startOffsetMs;
      currentIndexRef.current = currentIndexRef.current === 0 ? 1 : 0;

      initializeRecorder(currentRef, elapsedTimeMs + (t1 - t0));

      const blob = new Blob(chunks, { type: AUDIO_MIME_TYPE });
      const arrayBuffer = await blob.arrayBuffer();
      const audioCtx = new window.AudioContext();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

      const maxDurationMs = audioBuffer.duration * 1000;
      const clampedEndOffsetMs = Math.min(
        endOffsetMs - currentMediaRecorderStartOffsetMs,
        maxDurationMs
      );
      const clampedStartOffsetMs = Math.max(
        0,
        Math.min(startOffsetMs - currentMediaRecorderStartOffsetMs, clampedEndOffsetMs)
      );

      const { sampleRate } = audioBuffer;
      const startSample = Math.floor((clampedStartOffsetMs / 1000) * sampleRate);
      const endSample = Math.floor((clampedEndOffsetMs / 1000) * sampleRate);
      const length = endSample - startSample;

      const channelData: Float32Array<ArrayBuffer>[] = [];
      for (let ch = 0; ch < audioBuffer.numberOfChannels; ch += 1) {
        channelData.push(audioBuffer.getChannelData(ch).slice(startSample, endSample));
      }
      const segmentBuffer = audioCtx.createBuffer(audioBuffer.numberOfChannels, length, sampleRate);
      for (let ch = 0; ch < channelData.length; ch += 1) {
        segmentBuffer.copyToChannel(channelData[ch], ch, 0);
      }

      await audioCtx.close();

      return bufferToWav(segmentBuffer);
    },
    [
      getCurrentRecorderRef,
      resetInactivityTimeout,
      stopRecorderAndCollectChunks,
      initializeRecorder,
    ]
  );

  return {
    startLocalRecording,
    stopLocalRecording,
    extractSegment,
  };
}
