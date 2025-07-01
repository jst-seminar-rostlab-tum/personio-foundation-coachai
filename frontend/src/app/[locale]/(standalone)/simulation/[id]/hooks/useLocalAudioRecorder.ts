/* eslint-disable no-param-reassign */
import { useRef, useState } from 'react';

type LocalAudioRecorder = {
  recorder: MediaRecorder;
  chunks: Blob[];
  startOffsetMs: number;
};

export function useLocalAudioRecorder() {
  const currentIndexRef = useRef(0);
  const recorderARef = useRef<LocalAudioRecorder | null>(null);
  const recorderBRef = useRef<LocalAudioRecorder | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const [localAudioUrls, setLocalAudioUrls] = useState<string[]>([]);

  function getCurrentRecorderRef() {
    return currentIndexRef.current === 0 ? recorderARef : recorderBRef;
  }
  function getBackupRecorderRef() {
    return currentIndexRef.current === 0 ? recorderBRef : recorderARef;
  }

  function stopRecorderAndCollectChunks(recorderObj: LocalAudioRecorder): Promise<Blob[]> {
    return new Promise((resolve) => {
      const { chunks } = recorderObj;
      function onDataAvailable(e: BlobEvent) {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      }
      function onStop() {
        recorderObj.recorder.removeEventListener('dataavailable', onDataAvailable);
        recorderObj.recorder.removeEventListener('stop', onStop);
        resolve([...chunks]);
      }
      recorderObj.recorder.addEventListener('dataavailable', onDataAvailable);
      recorderObj.recorder.addEventListener('stop', onStop);
      recorderObj.recorder.stop();
    });
  }

  const startLocalRecording = (stream: MediaStream): void => {
    if (recorderARef.current && recorderBRef.current) return;
    localStreamRef.current = stream;
    initializeRecorder(recorderARef, 0);
    initializeRecorder(recorderBRef, 0);
    currentIndexRef.current = 0;
  };

  const initializeRecorder = (
    recorderRef: React.RefObject<LocalAudioRecorder | null>,
    startOffsetMs: number
  ): void => {
    if (recorderRef.current) {
      recorderRef.current.recorder.stop();
    }

    if (localStreamRef.current === null) return;

    const newRecorder: LocalAudioRecorder = {
      recorder: new MediaRecorder(localStreamRef.current, { mimeType: 'audio/webm' }),
      chunks: [],
      startOffsetMs,
    };

    newRecorder.recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data.size > 0) newRecorder.chunks.push(e.data);
    };

    newRecorder.recorder.start();
    recorderRef.current = newRecorder;
  };

  const stopLocalRecording = (): void => {
    [recorderARef, recorderBRef].forEach((ref) => {
      if (ref.current) {
        ref.current.recorder.stop();
        ref.current.chunks = [];
      }
    });
  };

  const extractSegment = async (
    startOffsetMs: number,
    endOffsetMs: number,
    elapsedTimeMs: number
  ): Promise<string> => {
    const currentRef = getCurrentRecorderRef();
    const backupRef = getBackupRecorderRef();
    if (!currentRef.current) return '';

    const stoppedRecorder = currentRef.current;
    const chunks = await stopRecorderAndCollectChunks(stoppedRecorder);
    const currentMediaRecorderStartOffsetMs = stoppedRecorder.startOffsetMs;

    currentIndexRef.current = currentIndexRef.current === 0 ? 1 : 0;

    initializeRecorder(backupRef, elapsedTimeMs);

    const blob = new Blob(chunks, { type: 'audio/webm' });
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
    const channelData: Float32Array[] = [];
    for (let ch = 0; ch < audioBuffer.numberOfChannels; ch += 1) {
      channelData.push(audioBuffer.getChannelData(ch).slice(startSample, endSample));
    }
    const segmentBuffer = audioCtx.createBuffer(audioBuffer.numberOfChannels, length, sampleRate);
    for (let ch = 0; ch < channelData.length; ch += 1) {
      segmentBuffer.copyToChannel(channelData[ch], ch, 0);
    }

    const wavBlob = await bufferToWav(segmentBuffer);
    const url = URL.createObjectURL(wavBlob);
    setLocalAudioUrls((prev) => [...prev, url]);
    return url;
  };

  async function bufferToWav(buffer: AudioBuffer): Promise<Blob> {
    const numOfChan = buffer.numberOfChannels;
    const length = buffer.length * numOfChan * 2 + 44;
    const bufferArray = new ArrayBuffer(length);
    const view = new DataView(bufferArray);

    let pos = 0;

    function setUint16(data: number): void {
      view.setUint16(pos, data, true);
      pos += 2;
    }

    function setUint32(data: number): void {
      view.setUint32(pos, data, true);
      pos += 4;
    }

    setUint32(0x46464952);
    setUint32(length - 8);
    setUint32(0x45564157);

    setUint32(0x20746d66);
    setUint32(16);
    setUint16(1);
    setUint16(numOfChan);
    setUint32(buffer.sampleRate);
    setUint32(buffer.sampleRate * 2 * numOfChan);
    setUint16(numOfChan * 2);
    setUint16(16);

    setUint32(0x61746164);
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
  }

  return {
    startLocalRecording,
    stopLocalRecording,
    extractSegment,
    localAudioUrls,
  };
}
