import { RotateCcwIcon, RotateCwIcon, PlayIcon, PauseIcon } from 'lucide-react';
import Slider from '@/components/ui/Slider';

interface AudioPlayerProps {
  currentTime: number;
  totalTime: number;
  setCurrentTime: (val: number) => void;
  isPlaying: boolean;
  setIsPlaying: (val: boolean) => void;
  formatTime: (seconds: number) => string;
  t: (key: string) => string;
}

export default function AudioPlayer({
  currentTime,
  totalTime,
  setCurrentTime,
  isPlaying,
  setIsPlaying,
  formatTime,
  t,
}: AudioPlayerProps) {
  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="text-xl text-bw-90 text-left w-full">{t('listenConversation')}</div>
      <div className="w-full border border-bw-20 rounded-lg p-6 flex flex-col items-center">
        <div className="flex gap-3 items-center w-full py-2">
          <Slider
            min={0}
            max={totalTime}
            value={[currentTime]}
            onValueChange={([val]) => setCurrentTime(val)}
            className="flex-1"
          />
        </div>
        <div className="flex flex-row justify-between w-full text-xs text-bw-50">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(totalTime)}</span>
        </div>
        <div className="flex items-center justify-center gap-8 w-full">
          <RotateCcwIcon
            className="w-8 h-8 cursor-pointer stroke-bw-40"
            strokeWidth={2}
            onClick={() => setCurrentTime(Math.max(0, currentTime - 10))}
            aria-label="Rewind 10 seconds"
          />
          <button
            className="w-16 h-16 rounded-full bg-marigold-40 flex items-center justify-center shadow-md"
            onClick={() => setIsPlaying(!isPlaying)}
            aria-label={isPlaying ? 'Pause' : 'Play'}
            type="button"
          >
            {isPlaying ? (
              <PauseIcon className="w-8 h-8" fill="white" color="white" />
            ) : (
              <PlayIcon className="w-8 h-8" fill="white" color="white" />
            )}
          </button>
          <RotateCwIcon
            className="w-8 h-8 cursor-pointer stroke-bw-40"
            strokeWidth={2}
            onClick={() => setCurrentTime(Math.min(totalTime, currentTime + 10))}
            aria-label="Fast forward 10 seconds"
          />
        </div>
      </div>
    </div>
  );
}
