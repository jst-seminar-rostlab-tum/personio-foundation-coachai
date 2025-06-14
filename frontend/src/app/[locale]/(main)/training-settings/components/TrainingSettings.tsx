'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Download } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import Switch from '@/components/ui/Switch';
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/AlertDialog';
import UserConfidenceFields from '@/components/common/UserConfidenceFields';
import { confidenceFields } from '@/configs/UserConfidenceFields.config';
import { useUserRoleLeadershipGoals } from '@/configs/UserRoleLeadershipGoals.config';
import { useDeleteUser } from '@/components/common/DeleteUserHandler';
import UserPreferences from './UserPreferences';

export default function TrainingSettings() {
  const [audioEnabled, setAudioEnabled] = useState(false);
  const t = useTranslations('TrainingSettings');
  const { handleDeleteUser, loading } = useDeleteUser();
  const userId = '0b222f0b-c7e5-4140-9049-35620fee8009';

  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="text-xl font-bold text-black">{t('title')}</div>
        <Link href="/dashboard">
          <Button>{t('backToDashboard')}</Button>
        </Link>
      </div>

      <div className="mt-6 space-y-4">
        <div className="w-full px-4 py-3 flex items-center rounded-t-lg">
          <Accordion type="multiple" className="w-full" defaultValue={['item-1', 'item-2']}>
            <AccordionItem value="item-1" className="text-dark">
              <AccordionTrigger className="font-bw-70 cursor-pointer">
                {t('privacyControls')}
              </AccordionTrigger>
              <AccordionContent>
                <div className="flex items-center justify-between w-full">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('storeAudioTranscripts')}</div>
                    <div className="text-bw-40">
                      {audioEnabled ? t('ninetyDays') : t('zeroDays')}
                    </div>
                  </div>
                  <div className="flex flex-col items-center">
                    <Switch checked={audioEnabled} onCheckedChange={setAudioEnabled} />
                  </div>
                </div>
                <div className="flex items-center justify-between w-full mt-4">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('exportData')}</div>
                  </div>
                  <div className="p-2 flex items-center">
                    <Button variant="outline" className="w-full">
                      <Download className="w-4 h-4" />
                      <span className="hidden sm:inline">{t('export')}</span>
                    </Button>
                  </div>
                </div>
                <div className="flex items-center justify-between w-full mt-4">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('deleteAccount')}</div>
                  </div>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">{t('requestDeletion')}</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>{t('deleteAccountConfirmTitle')}</AlertDialogTitle>
                        <AlertDialogDescription>
                          {t('deleteAccountConfirmDesc')}
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>{t('cancel')}</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => handleDeleteUser(userId)}
                          disabled={loading}
                        >
                          {loading ? t('deleting') : t('confirm')}
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-2" className="text-dark">
              <AccordionTrigger className="font-bw-70 cursor-pointer">
                {t('personalizationSettings')}
              </AccordionTrigger>
              <AccordionContent>
                <UserPreferences
                  className="flex flex-col gap-5 px-2"
                  preferences={useUserRoleLeadershipGoals()}
                />
                <hr className="my-9.5 border-gray-200" />
                <UserConfidenceFields
                  className="flex flex-col gap-5 px-2"
                  fields={confidenceFields}
                />
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
      <Button size="full">{t('saveSettings')}</Button>
    </div>
  );
}
