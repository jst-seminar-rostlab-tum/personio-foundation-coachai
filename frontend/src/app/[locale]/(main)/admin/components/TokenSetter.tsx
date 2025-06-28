'use client';

import { useTranslations } from 'next-intl';
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { adminService } from '@/services/client/AdminService';
import { showSuccessToast, showErrorToast } from '@/lib/toast';

interface TokenSetterProps {
  dailyTokenLimit: number;
}

export default function TokenSetter({ dailyTokenLimit }: TokenSetterProps) {
  const t = useTranslations('Admin');
  const [tokenLimit, setTokenLimit] = useState<number>(dailyTokenLimit);
  const [savedTokenLimit, setSavedTokenLimit] = useState<number>(dailyTokenLimit);
  const [saving, setSaving] = useState(false);

  const hasTokenLimitChanged = tokenLimit !== savedTokenLimit;

  const handleSaveTokenLimit = async () => {
    if (!Number.isInteger(tokenLimit) || tokenLimit < 1) {
      showErrorToast(null, t('tokenNumberFailed'));
      return;
    }
    setSaving(true);
    try {
      await adminService.updateDailyUserTokenLimit(tokenLimit);
      showSuccessToast(t('tokenSuccess'));
      setSavedTokenLimit(tokenLimit);
    } catch (error) {
      showErrorToast(error, t('tokenFailed'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full max-w-md mb-8 text-left">
      <label className="block text-bw-70 font-semibold text-sm mb-1">
        {t('tokensPerUserLabel')}
      </label>
      <div className="flex gap-2 items-center">
        <Input
          type="number"
          min={1}
          value={tokenLimit}
          onChange={(e) => setTokenLimit(Number(e.target.value))}
          disabled={saving}
        />
        <Button
          onClick={handleSaveTokenLimit}
          disabled={saving || !hasTokenLimitChanged}
          variant={saving || !hasTokenLimitChanged ? 'disabled' : 'default'}
        >
          {saving ? t('saving') : t('save')}
        </Button>
      </div>
    </div>
  );
}
