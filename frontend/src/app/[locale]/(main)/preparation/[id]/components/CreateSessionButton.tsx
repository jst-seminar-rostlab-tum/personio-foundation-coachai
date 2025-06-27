'use client';

import { Button } from '@/components/ui/Button';
import { sessionService } from '@/services/client/SessionService';
import { Play } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { CreateSessionButtonProps } from '@/interfaces/CreateSessionButtonProps';
import { useRouter } from 'next/navigation';
import { showErrorToast } from '@/lib/toast';
import { useState } from 'react';

export const CreateSessionButton = ({ scenarioId }: CreateSessionButtonProps) => {
  const t = useTranslations('Preparation');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreateSession = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      const { data } = await sessionService.createSession(scenarioId);
      router.push(`/simulation/${data.id}`);
    } catch (error) {
      showErrorToast(error, t('sessionCreationError'));
      setIsSubmitting(false);
    }
  };

  return (
    <Button
      onClick={handleCreateSession}
      size="full"
      variant={isSubmitting ? 'disabled' : 'default'}
      disabled={isSubmitting}
    >
      <Play />
      {isSubmitting ? tCommon('starting') : tCommon('start')}
    </Button>
  );
};
