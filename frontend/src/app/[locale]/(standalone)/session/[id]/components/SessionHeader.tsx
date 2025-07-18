'use client';

import { User } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { useTranslations } from 'next-intl';
import { ConnectionStatus } from '@/interfaces/models/Session';
import { Categories } from '@/lib/constants/categories';

interface SessionHeaderProps {
  characterName: string;
  sessionLabel: string;
  time: number;
  connectionStatus?: ConnectionStatus;
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

function getConnectionStatusColor(status: ConnectionStatus) {
  switch (status) {
    case ConnectionStatus.Connected:
      return 'bg-forest-50';
    case ConnectionStatus.Connecting:
      return 'bg-marigold-50';
    case ConnectionStatus.Disconnected:
    case ConnectionStatus.Closed:
    case ConnectionStatus.Failed:
      return 'bg-flame-50';
    default:
      return 'bg-bw-30';
  }
}

export default function SessionHeader({
  characterName,
  sessionLabel,
  time = 0,
  connectionStatus,
}: SessionHeaderProps) {
  const t = useTranslations('Session');
  const tConversationScenario = useTranslations('ConversationScenario');
  const tCategories = useTranslations('ConversationScenario.categories');
  const categories = Categories(tCategories);

  return (
    <div className="relative border-b border-bw-10 w-full">
      <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto px-[clamp(1.25rem,4vw,4rem)]">
        <div className="flex items-center justify-between">
          <Badge variant="default" className="bg-marigold-30/40 text-marigold-90">
            {categories[sessionLabel].name}
          </Badge>
          <div className="flex items-center gap-3">
            {connectionStatus && (
              <Badge variant="outline" className="flex items-center gap-1.5">
                <div
                  className={`w-2 h-2 rounded-full ${getConnectionStatusColor(connectionStatus)}`}
                ></div>
                <span>
                  {connectionStatus === ConnectionStatus.Connecting && t('connecting')}
                  {connectionStatus === ConnectionStatus.Connected && t('connected')}
                  {[
                    ConnectionStatus.Disconnected,
                    ConnectionStatus.Closed,
                    ConnectionStatus.Failed,
                  ].includes(connectionStatus) && t('disconnected')}
                </span>
              </Badge>
            )}
            <Badge variant="outline" className="w-16 text-center justify-center">
              {formatTime(time)}
            </Badge>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Avatar className="border-marigold-50 border-1">
            <AvatarImage
              src={tConversationScenario(`customize.persona.personas.${characterName}.imageUri`)}
              alt={`${tConversationScenario(
                `customize.persona.personas.${characterName}.name`
              )} avatar`}
            />
            <AvatarFallback>
              <User className="w-4 h-4" />
            </AvatarFallback>
          </Avatar>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-md text-bw-90">
                {tConversationScenario(`customize.persona.personas.${characterName}.name`)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
