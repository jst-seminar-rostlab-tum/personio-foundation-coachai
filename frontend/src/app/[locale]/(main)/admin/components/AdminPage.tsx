'use client';

import { ChevronDown, Search, Trash2 } from 'lucide-react';
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/AlertDialog';
import { AdminProps } from '@/interfaces/AdminProps';
import { adminService } from '@/services/client/AdminService';
import { showSuccessToast, showErrorToast } from '@/lib/toast';
import Reviews from './Reviews';

export default function Admin({ stats, reviews }: AdminProps) {
  const t = useTranslations('Admin');
  const tr = useTranslations('Settings');
  const [tokenLimit, setTokenLimit] = useState<number>(stats.dailyTokenLimit);
  const [saving, setSaving] = useState(false);
  const [visibleUsers, setVisibleUsers] = useState(5);

  const statsArray = [
    { value: stats.totalUsers, label: t('statActiveUsers') },
    { value: stats.totalTrainings, label: t('statTotalTrainings') },
    { value: stats.totalReviews, label: t('statReviews') },
    { value: `${stats.averageScore}%`, label: t('statAverageScore') },
  ];

  const handleLoadMore = () => setVisibleUsers((v) => Math.min(v + 5, allUsers.length));

  const handleSaveTokenLimit = async () => {
    if (!Number.isInteger(tokenLimit) || tokenLimit < 1) {
      showErrorToast(null, t('tokenNumberFailed'));
      return;
    }
    setSaving(true);
    try {
      await adminService.updateDailyUserTokenLimit(tokenLimit);
      showSuccessToast(t('tokenSuccess'));
    } catch (error) {
      showErrorToast(error, t('tokenFailed'));
    } finally {
      setSaving(false);
    }
  };

  const allUsers = [
    'Sara P.',
    'TheLegend27',
    'Jackson Lopez',
    'Maria Surname',
    'Alex Kim',
    'John Doe',
    'Jane Roe',
    'Chris Evans',
    'Sam Lee',
    'Patricia Surname',
  ];

  const canLoadMore = visibleUsers < allUsers.length;

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
          <Button onClick={handleSaveTokenLimit} disabled={saving}>
            {saving ? t('saving') : t('save')}
          </Button>
        </div>
      </div>
      <Reviews {...reviews} />
      <Accordion type="multiple" className="w-full mt-8">
        <AccordionItem value="item-1" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('userManagement')}
          </AccordionTrigger>
          <AccordionContent>
            <div className="mb-4">
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-bw-40">
                  <Search className="w-4 h-4" />
                </span>
                <Input
                  type="text"
                  placeholder={t('search')}
                  className="w-full pl-10 pr-3 py-2 border border-bw-20 rounded text-sm text-bw-70 placeholder-bw-40 focus:border-bw-20 focus-visible:outline-none focus-visible:ring-0"
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm table-fixed">
                <colgroup>
                  <col style={{ width: '70%' }} />
                  <col style={{ width: '30%' }} />
                </colgroup>
                <thead>
                  <tr>
                    <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('users')}</th>
                    <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {allUsers.slice(0, visibleUsers).map((user) => (
                    <tr key={user} className="border-t border-bw-10">
                      <td className="py-2 px-2 truncate">{user}</td>
                      <td className="py-2 px-2">
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={t('deleteUser')}
                              className="group"
                            >
                              <Trash2 className="w-4 h-4 text-bw-40 group-hover:text-flame-50" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>{tr('deleteAccountConfirmTitle')}</AlertDialogTitle>
                              <AlertDialogDescription>
                                {tr('deleteAccountConfirmDesc', { user })}
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>{tr('cancel')}</AlertDialogCancel>
                              <AlertDialogAction>{tr('confirm')}</AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {canLoadMore && (
              <div className="flex justify-center mt-4">
                <Button variant="ghost" onClick={handleLoadMore}>
                  {t('loadMore')} <ChevronDown className="ml-2 w-4 h-4" />
                </Button>
              </div>
            )}
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-2" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('trainingCategories')}
          </AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-3" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('trainingScenarios')}
          </AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
