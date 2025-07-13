import { useRef, useEffect, useState } from 'react';
import { RotateCcwIcon, RotateCwIcon, PlayIcon, PauseIcon } from 'lucide-react';
import Slider from '@/components/ui/Slider';

interface AudioPlayerProps {
  currentTime: number;
  setCurrentTime: React.Dispatch<React.SetStateAction<number>>;
  isPlaying: boolean;
  setIsPlaying: React.Dispatch<React.SetStateAction<boolean>>;
  fullAudioUrl: string | null;
  formatTime: (seconds: number) => string;
  t: (key: string) => string;
}

export default function AudioPlayer({
  currentTime,
  setCurrentTime,
  isPlaying,
  setIsPlaying,
  formatTime,
  fullAudioUrl,
  t,
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [totalTime, setTotalTime] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const wasPlayingBeforeDrag = useRef(false);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.play();
    } else {
      audio.pause();
    }
  }, [isPlaying]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (Math.abs(audio.currentTime - currentTime) > 1) {
      audio.currentTime = currentTime;
    }
  }, [currentTime]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return undefined;
    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };
    const handleLoadedMetadata = () => {
      setTotalTime(audio.duration);
    };
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(audio.duration);
    };
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [setCurrentTime, setIsPlaying]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isDragging) {
      wasPlayingBeforeDrag.current = isPlaying;
      if (isPlaying) {
        setIsPlaying(false);
      }
    }
    if (!isDragging && wasPlayingBeforeDrag.current) {
      setIsPlaying(true);
    }
  }, [isDragging, isPlaying, setIsPlaying]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        (e.target as HTMLElement)?.tagName === 'INPUT' ||
        (e.target as HTMLElement)?.tagName === 'TEXTAREA'
      ) {
        return;
      }
      if (e.code === 'ArrowRight') {
        setCurrentTime((prev) => Math.min(totalTime, prev + 10));
        e.preventDefault();
      } else if (e.code === 'ArrowLeft') {
        setCurrentTime((prev) => Math.max(0, prev - 10));
        e.preventDefault();
      } else if (e.code === 'Space') {
        setIsPlaying((prev) => !prev);
        e.preventDefault();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [setCurrentTime, setIsPlaying, totalTime, isPlaying]);

  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="text-xl text-bw-90 text-left w-full">{t('listenConversation')}</div>
      <div className="w-full border border-bw-20 rounded-lg p-6 flex flex-col items-center">
        {fullAudioUrl ? (
          <>
            <audio ref={audioRef} src={fullAudioUrl} style={{ display: 'none' }} />
            <div className="flex gap-3 items-center w-full py-2">
              <Slider
                min={0}
                max={totalTime}
                value={[currentTime]}
                onValueChange={([val]) => setCurrentTime(val)}
                onPointerDown={() => setIsDragging(true)}
                onPointerUp={() => setIsDragging(false)}
                className="flex-1"
              />
            </div>
            <div className="flex flex-row justify-between w-full text-xs text-bw-50">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(totalTime)}</span>
            </div>
            <div className="flex items-center justify-center gap-8 w-full">
              <button
                type="button"
                className="w-12 h-12 rounded-full flex items-center justify-center cursor-pointer transition-colors duration-300 hover:bg-bw-10"
                onClick={() => setCurrentTime(Math.max(0, currentTime - 10))}
                aria-label="Rewind 10 seconds"
              >
                <RotateCcwIcon className="w-6 h-6 stroke-bw-40" strokeWidth={2} />
              </button>
              <button
                className="w-12 h-12 rounded-full bg-marigold-40 flex items-center justify-center cursor-pointer transition-colors duration-300 hover:bg-marigold-50"
                onClick={() => setIsPlaying(!isPlaying)}
                aria-label={isPlaying ? 'Pause' : 'Play'}
                type="button"
              >
                {isPlaying ? (
                  <PauseIcon className="w-6 h-6" fill="white" color="white" />
                ) : (
                  <PlayIcon className="w-6 h-6" fill="white" color="white" />
                )}
              </button>
              <button
                type="button"
                className="w-12 h-12 rounded-full flex items-center justify-center cursor-pointer transition-colors duration-300 hover:bg-bw-10"
                onClick={() => setCurrentTime(Math.min(totalTime, currentTime + 10))}
                aria-label="Fast forward 10 seconds"
              >
                <RotateCwIcon className="w-6 h-6 stroke-bw-40" strokeWidth={2} />
              </button>
            </div>
          </>
        ) : (
          <div className="text-center">{t('audioUnavailable')}</div>
        )}
      </div>
    </div>
  );
}
