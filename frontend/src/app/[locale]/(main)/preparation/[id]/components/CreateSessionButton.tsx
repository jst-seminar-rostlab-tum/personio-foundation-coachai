'use client';

import { Button } from '@/components/ui/Button';
import { sessionService } from '@/services/client/SessionService';
import { Play } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { CreateSessionButtonProps } from '@/interfaces/CreateSessionButtonProps';
import { useRouter } from 'next/navigation';
import { showErrorToast } from '@/lib/toast';

export const CreateSessionButton = ({ scenarioId }: CreateSessionButtonProps) => {
  const t = useTranslations('Preparation');
  const router = useRouter();

  const handleCreateSession = async () => {
    try {
      const { data } = await sessionService.createSession(scenarioId);
      router.push(`/simulation/${data.id}`);
    } catch (error) {
      showErrorToast(error, t('sessionCreationError'));
    }
  };

  return (
    <Button onClick={handleCreateSession} size="full">
      <Play />
      {t('navigation.start')}
    </Button>
  );
};
