'use client';

import { Button } from '@/components/ui/Button';
import { sessionService } from '@/services/SessionService';
import { Play } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { showErrorToast } from '@/lib/component-utils/toast';
import { useState } from 'react';
import { api } from '@/services/ApiClient';

interface CreateSessionButtonProps {
  scenarioId: string;
}

export const CreateSessionButton = ({ scenarioId }: CreateSessionButtonProps) => {
  const t = useTranslations('Preparation');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreateSession = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      const { data } = await sessionService.createSession(api, scenarioId);
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
