'use client';

import { User } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';

interface SimulationHeaderProps {
  characterName?: string;
  characterRole?: string;
  characterDescription?: string;
  sessionLabel?: string;
  avatarSrc?: string;
  time: number;
}

function formatTime(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s
      .toString()
      .padStart(2, '0')}`;
  }
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

export default function SimulationHeader({
  characterName = 'Alex',
  characterRole = 'Team Member',
  characterDescription = 'Defensive at first, but open to feedback',
  sessionLabel = 'Performance Reviews',
  avatarSrc,
  time = 0,
}: SimulationHeaderProps) {
  return (
    <div className="flex flex-col gap-6 p-6 border-b border-bw-10">
      <div className="flex items-center justify-between">
        <Badge variant="default" className="bg-marigold-30/40 text-marigold-90">
          {sessionLabel}
        </Badge>
        <Badge variant="outline" className="w-16 text-center justify-center">
          {formatTime(time)}
        </Badge>
      </div>
      <div className="flex items-center gap-4">
        <Avatar>
          <AvatarImage src={avatarSrc} alt={`${characterName} avatar`} />
          <AvatarFallback>
            <User className="w-4 h-4" />
          </AvatarFallback>
        </Avatar>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-md text-gray-900">{characterName}</span>
            <span className="text-md text-gray-700 font-normal">({characterRole})</span>
          </div>
          <div className="text-xs text-bw-40 leading-tight">{characterDescription}</div>
        </div>
      </div>
    </div>
  );
}
