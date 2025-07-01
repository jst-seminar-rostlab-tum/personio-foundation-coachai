import { useRef, useState } from 'react';

export function useLocalAudioRecorder() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [localAudioUrls, setLocalAudioUrls] = useState<string[]>([]);

  const startLocalRecording = (stream: MediaStream): void => {
    if (mediaRecorderRef.current) return;

    chunksRef.current = [];
    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.start(100);
  };

  const stopLocalRecording = (): void => {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;
  };

  const extractSegment = async (startOffsetMs: number, endOffsetMs: number): Promise<string> => {
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
    const arrayBuffer = await blob.arrayBuffer();
    const audioCtx = new window.AudioContext();
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

    const maxDurationMs = audioBuffer.duration * 1000;
    const clampedEndOffsetMs = Math.min(endOffsetMs, maxDurationMs);
    const clampedStartOffsetMs = Math.max(0, Math.min(startOffsetMs, clampedEndOffsetMs));

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
