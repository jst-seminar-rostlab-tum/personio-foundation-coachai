'use client';

import { useTranslations } from 'next-intl';
import React, { useState } from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { Button } from '@/components/ui/Button';
import StatCard from '@/components/common/StatCard';
import Input from '@/components/ui/Input';
import { AdminProps } from '@/interfaces/AdminProps';
import { adminService } from '@/services/client/AdminService';
import { showSuccessToast, showErrorToast } from '@/lib/toast';
import Reviews from './Reviews';
import UsersList from './UsersList';

export default function Admin({ stats, reviews, users }: AdminProps) {
  const t = useTranslations('Admin');
  const [tokenLimit, setTokenLimit] = useState<number>(stats.dailyTokenLimit);
  const [savedTokenLimit, setSavedTokenLimit] = useState<number>(stats.dailyTokenLimit);
  const [saving, setSaving] = useState(false);

  const hasTokenLimitChanged = tokenLimit !== savedTokenLimit;

  const statsArray = [
    { value: stats.totalUsers, label: t('statActiveUsers') },
    { value: stats.totalTrainings, label: t('statTotalTrainings') },
    { value: stats.totalReviews, label: t('statReviews') },
    { value: `${stats.averageScore}%`, label: t('statAverageScore') },
  ];

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
    <div className="max-w-full">
      <div className="text-2xl font-bold text-bw-70 text-center mb-2">{t('dashboardTitle')}</div>
      <div className="text-sm text-bw-40 text-center mb-8">{t('dashboardSubtitle')}</div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statsArray.map((stat, i) => (
          <StatCard key={i} value={stat.value} label={stat.label} />
        ))}
      </div>
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
      <Reviews {...reviews} />
      <Accordion type="multiple">
        <AccordionItem value="item-1">
          <AccordionTrigger>{t('userManagement')}</AccordionTrigger>
          <AccordionContent>
            <UsersList
              initialUsers={users.users.map((u) => ({
                ...u,
                id: u.userId,
              }))}
              totalCount={users.totalCount}
              initialPage={1}
              pageSize={10}
            />
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2">
          <AccordionTrigger>{t('trainingCategories')}</AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-3">
          <AccordionTrigger>{t('trainingScenarios')}</AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
