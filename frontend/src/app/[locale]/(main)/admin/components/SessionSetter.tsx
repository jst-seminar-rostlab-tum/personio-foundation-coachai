'use client';

import { useTranslations } from 'next-intl';
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { adminService } from '@/services/AdminService';
import { showSuccessToast, showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';

interface SessionSetterProps {
  dailySessionLimit: number;
}

export default function SessionSetter({ dailySessionLimit }: SessionSetterProps) {
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');
  const [sessionLimit, setSessionLimit] = useState<number>(dailySessionLimit);
  const [savedSessionLimit, setSavedSessionLimit] = useState<number>(dailySessionLimit);
  const [saving, setSaving] = useState(false);

  const hasSessionLimitChanged = sessionLimit !== savedSessionLimit;

  const handleSaveSessionLimit = async () => {
    if (!Number.isInteger(sessionLimit) || sessionLimit < 1) {
      showErrorToast(null, t('sessionNumberFailed'));
      return;
    }
    setSaving(true);
    try {
      await adminService.updateDailyUserSessionLimit(api, sessionLimit);
      showSuccessToast(t('sessionSuccess'));
      setSavedSessionLimit(sessionLimit);
    } catch (error) {
      showErrorToast(error, t('sessionFailed'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full max-w-md mb-8 text-left">
      <label className="block text-bw-70 font-semibold text-sm mb-1">
        {t('sessionsPerUserLabel')}
      </label>
      <div className="flex gap-2 items-center">
        <Input
          type="number"
          min={1}
          value={sessionLimit}
          onChange={(e) => setSessionLimit(Number(e.target.value))}
          disabled={saving}
        />
        <Button
          onClick={handleSaveSessionLimit}
          disabled={saving || !hasSessionLimitChanged}
          variant={saving || !hasSessionLimitChanged ? 'disabled' : 'default'}
        >
          {saving ? tCommon('saving') : tCommon('save')}
        </Button>
      </div>
    </div>
  );
}
