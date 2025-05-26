'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Download } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import Switch from '@/components/ui/switch';
import UserPreferences from '@/components/layout/UserPreferences';
import UserConfidenceFields from '@/components/layout/UserConfidenceFields';
import { useUserConfidenceFields } from '@/configs/UserConfidenceFields.config';
import { useUserPreferences } from '@/configs/UserPreferences.config';
import { useUserRoleLeadershipGoals } from '@/configs/UserRoleLeadershipGoals.config';

export default function TrainingSettingsPage() {
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [transcriptEnabled, setTranscriptEnabled] = useState(false);
  const t = useTranslations('TrainingSettings');

  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="text-xl font-bold text-black">{t('title')}</div>
        <Link href="/dashboard">
          <Button className="px-3 py-2 text-sm">{t('backToDashboard')}</Button>
        </Link>
      </div>

      {/* Accordion Sections */}
      <div className="mt-6 space-y-4">
        <div className="w-full px-4 py-3 flex items-center rounded-t-lg">
          <Accordion type="multiple" className="w-full">
            <AccordionItem value="item-1" className="text-dark">
              <AccordionTrigger className="font-bw-70">{t('privacyControls')}</AccordionTrigger>
              <AccordionContent>
                <div className="flex items-start justify-between w-full">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('storeAudio')}</div>
                    <div className="text-bw-40">{t('storeAudioDesc')}</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <Switch checked={audioEnabled} onCheckedChange={setAudioEnabled} />
                    <div className="text-xs mt-2 text-center">
                      {audioEnabled ? t('ninetyDays') : t('zeroDays')}
                    </div>
                  </div>
                </div>
                <div className="flex items-start justify-between w-full mt-4">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('storeTranscript')}</div>
                    <div className="text-bw-40">{t('storeTranscriptDesc')}</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <Switch checked={transcriptEnabled} onCheckedChange={setTranscriptEnabled} />
                    <div className="text-xs mt-2 text-center">
                      {transcriptEnabled ? t('ninetyDays') : t('zeroDays')}
                    </div>
                  </div>
                </div>
                <div className="flex items-start justify-between w-full mt-4">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('exportData')}</div>
                    <div className="text-bw-40">{t('exportDataDesc')}</div>
                  </div>
                  <Button variant="outline" className="flex items-center gap-2 px-3 py-2 text-sm">
                    <Download className="w-4 h-4" />
                    <span className="hidden sm:inline">{t('export')}</span>
                  </Button>
                </div>
                <div className="flex items-start justify-between w-full mt-4">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('deleteAccount')}</div>
                    <div className="text-bw-40">{t('deleteAccountDesc')}</div>
                  </div>
                  <Button className="px-3 py-2 text-sm" variant={'destructive'}>
                    {' '}
                    {t('requestDeletion')}{' '}
                  </Button>
                </div>
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-2" className="text-dark">
              <AccordionTrigger className="font-bw-70">
                {t('personalizationSettings')}
              </AccordionTrigger>
              <AccordionContent>
                <UserPreferences
                  className="md:w-1/2 flex flex-col gap-5 px-2"
                  preferences={useUserRoleLeadershipGoals()}
                />
                <hr className="my-9.5 border-gray-200" />
                <UserConfidenceFields
                  className="md:w-1/2 flex flex-col gap-5 px-2"
                  fields={useUserConfidenceFields()}
                />
                <hr className="my-9.5 border-gray-200" />
                <UserPreferences
                  className="md:w-1/2 flex flex-col gap-5 px-2"
                  preferences={useUserPreferences()}
                />
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
      <div className="mt-8 w-full flex justify-center sm:justify-end">
        <Button className="w-full sm:w-auto px-3 py-2 text-sm">{t('saveSettings')}</Button>
      </div>
    </div>
  );
}
