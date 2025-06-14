'use client';

import React, { use, useState } from 'react';
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
import { UserProfileService } from '@/services/UserProfileService';
import { UserPreference } from '@/interfaces/UserInputFields';
import { PrimaryGoals, UserRoles } from '@/lib/utils';
import { UserProfile } from '@/interfaces/UserProfile';
import UserPreferences from './UserPreferences';

export default function TrainingSettings({ userProfile }: { userProfile: Promise<UserProfile> }) {
  const t = useTranslations('TrainingSettings');
  const tOptions = useTranslations('TrainingSettings.leadershipGoals');
  const userProfileData = use(userProfile);
  const [storeConversations, setStoreConversations] = useState(userProfileData.storeConversations);
  const [currentRole, setCurrentRole] = useState(userProfileData.professionalRole);
  const [primaryGoal, setPrimaryGoal] = useState(
    userProfileData.goals.length > 0 ? userProfileData.goals[0] : ''
  );

  const getConfidenceScores = (area: string) => {
    const score = userProfileData.confidenceScores?.find(
      (confidenceScore) => confidenceScore.confidenceArea === area
    )?.score;
    return score !== undefined ? [score] : [50];
  };

  const [difficulty, setDifficulty] = useState(getConfidenceScores('giving_difficult_feedback'));
  const [conflict, setConflict] = useState(getConfidenceScores('managing_team_conflicts'));
  const [conversation, setConversation] = useState(
    getConfidenceScores('leading_challenging_conversations')
  );
  const confidenceFieldsProps = {
    difficulty,
    conflict,
    conversation,
    setDifficulty,
    setConflict,
    setConversation,
  };

  const userPreferences: UserPreference[] = [
    {
      label: tOptions('currentRole.label'),
      options: UserRoles(),
      value: currentRole,
      defaultValue: 'team_leader',
      onChange: (value: string) => {
        setCurrentRole(value);
      },
    },
    {
      label: tOptions('primaryGoals.label'),
      options: PrimaryGoals(),
      value: primaryGoal,
      defaultValue: 'managing_team_conflicts',
      onChange: (value: string) => {
        setPrimaryGoal(value);
      },
    },
  ];

  const handleSaveSettings = async () => {
    try {
      await UserProfileService.updateUserProfile({
        storeConversations,
        professionalRole: currentRole,
        goals: [primaryGoal],
        /* As soon as the backend supports confidence scores patch, we can uncomment this
        confidenceScores: [
          { confidenceArea: 'giving_difficult_feedback', score: difficulty[0] },
          { confidenceArea: 'managing_team_conflicts', score: conflict[0] },
          { confidenceArea: 'leading_challenging_conversations', score: conversation[0] },
        ], */
      });
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };
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
                      {storeConversations ? t('ninetyDays') : t('zeroDays')}
                    </div>
                  </div>
                  <div className="flex flex-col items-center">
                    <Switch checked={storeConversations} onCheckedChange={setStoreConversations} />
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
                        <AlertDialogAction>{t('confirm')}</AlertDialogAction>
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
                  preferences={userPreferences}
                />
                <hr className="my-9.5 border-gray-200" />
                <UserConfidenceFields
                  {...confidenceFieldsProps}
                  className="flex flex-col gap-5 px-2"
                />
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>
      <Button size="full" onClick={handleSaveSettings}>
        {t('saveSettings')}
      </Button>
    </div>
  );
}
