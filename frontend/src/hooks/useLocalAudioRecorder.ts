import { useRef, useState } from 'react';

export function useLocalAudioRecorder() {
  const recorderARef = useRef<MediaRecorder | null>(null);
  const recorderBRef = useRef<MediaRecorder | null>(null);
  const chunksARef = useRef<Blob[]>([]);
  const chunksBRef = useRef<Blob[]>([]);
  const localStreamRef = useRef<MediaStream | null>(null);

  const activeIndexRef = useRef<0 | 1>(0); // 0 = A, 1 = B
  const offsetMsRef = useRef<number>(0);
  const [localAudioUrls, setLocalAudioUrls] = useState<string[]>([]);

  // Utility: Get current/idle recorder and chunks
  const getActiveChunks = () =>
    activeIndexRef.current === 0 ? chunksARef.current : chunksBRef.current;

  const startLocalRecording = (stream: MediaStream): void => {
    if (recorderARef.current || recorderBRef.current) return;
    localStreamRef.current = stream;
    // Start with recorder A
    startRecorder(0);
  };

  const startRecorder = (index: 0 | 1) => {
    if (!localStreamRef.current) return;
    const chunksRef = index === 0 ? chunksARef : chunksBRef;
    chunksRef.current = [];

    const recorder = new MediaRecorder(localStreamRef.current, { mimeType: 'audio/webm' });
    recorder.ondataavailable = (e: BlobEvent) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    recorder.start(100);

    if (index === 0) recorderARef.current = recorder;
    else recorderBRef.current = recorder;
  };

  const stopRecorder = (index: 0 | 1) => {
    if (index === 0) {
      recorderARef.current?.stop();
      recorderARef.current = null;
    } else {
      recorderBRef.current?.stop();
      recorderBRef.current = null;
    }
  };

  // This is the gapless extractSegment function!
  const extractSegment = async (startOffsetMs: number, endOffsetMs: number): Promise<string> => {
    // 1. Start the idle recorder before stopping the active one (seamless!)
    const nextIndex: 0 | 1 = activeIndexRef.current === 0 ? 1 : 0;
    startRecorder(nextIndex);

    // 2. Get current active chunks and offset
    const chunks = [...getActiveChunks()];
    const offsetMs = offsetMsRef.current;

    // 3. Stop the active recorder (now idle)
    stopRecorder(activeIndexRef.current);

    // 4. Swap active index and offset
    offsetMsRef.current = endOffsetMs;
    activeIndexRef.current = nextIndex;

    // 5. Process the extracted audio from the stopped recorder
    const blob = new Blob(chunks, { type: 'audio/webm' });
    const arrayBuffer = await blob.arrayBuffer();
    const audioCtx = new window.AudioContext();
    const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

    const maxDurationMs = audioBuffer.duration * 1000;
    const clampedEndOffsetMs = Math.min(endOffsetMs - offsetMs, maxDurationMs);
    const clampedStartOffsetMs = Math.max(
      0,
      Math.min(startOffsetMs - offsetMs, clampedEndOffsetMs)
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

  const stopLocalRecording = (): void => {
    stopRecorder(0);
    stopRecorder(1);
    recorderARef.current = null;
    recorderBRef.current = null;
  };

  async function bufferToWav(buffer: AudioBuffer): Promise<Blob> {
    const numOfChan = buffer.numberOfChannels;
    const length = buffer.length * numOfChan * 2 + 44;
    const bufferArray = new ArrayBuffer(length);
    const view = new DataView(bufferArray);

    // Write WAV header
    let pos = 0;
    function setUint16(data: number): void {
      view.setUint16(pos, data, true);
      pos += 2;
    }
    function setUint32(data: number): void {
      view.setUint32(pos, data, true);
      pos += 4;
    }
    setUint32(0x46464952); // "RIFF"
    setUint32(length - 8); // file length - 8
    setUint32(0x45564157); // "WAVE"
    setUint32(0x20746d66); // "fmt " chunk
    setUint32(16); // length = 16
    setUint16(1); // PCM (uncompressed)
    setUint16(numOfChan);
    setUint32(buffer.sampleRate);
    setUint32(buffer.sampleRate * 2 * numOfChan);
    setUint16(numOfChan * 2);
    setUint16(16);
    setUint32(0x61746164); // "data" - chunk
    setUint32(length - pos - 4);

    // Write interleaved PCM samples
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
