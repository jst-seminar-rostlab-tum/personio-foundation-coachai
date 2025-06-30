'use client';

import React, { use, useState } from 'react';
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
import UserConfidenceFields from '@/components/common/UserConfidenceFields';
import { DeleteUserHandler } from '@/components/common/DeleteUserHandler';
import { UserProfileService } from '@/services/UserProfileService';
import { UserPreference } from '@/interfaces/models/UserInputFields';
import { PrimaryGoals, UserRoles } from '@/lib/utils';
import { UserProfile } from '@/interfaces/models/UserProfile';
import { showErrorToast, showSuccessToast } from '@/lib/toast';
import UserPreferences from './UserPreferences';

interface SettingsProps {
  userProfile: Promise<UserProfile>;
}

const getConfidenceScores = (userProfileData: UserProfile, area: string) => {
  const score = userProfileData.confidenceScores?.find(
    (confidenceScore) => confidenceScore.confidenceArea === area
  )?.score;
  return score !== undefined ? [score] : [50];
};

export default function Settings({ userProfile }: SettingsProps) {
  const t = useTranslations('Settings');
  const tOptions = useTranslations('Settings.leadershipGoals');
  const userProfileData = use(userProfile);

  const [storeConversations, setStoreConversations] = useState(
    userProfileData.storeConversations ?? false
  );
  const [currentRole, setCurrentRole] = useState(userProfileData.professionalRole);
  const [primaryGoals, setPrimaryGoals] = useState(userProfileData.goals);
  const [difficulty, setDifficulty] = useState(
    getConfidenceScores(userProfileData, 'giving_difficult_feedback')
  );
  const [conflict, setConflict] = useState(
    getConfidenceScores(userProfileData, 'managing_team_conflicts')
  );
  const [conversation, setConversation] = useState(
    getConfidenceScores(userProfileData, 'leading_challenging_conversations')
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [savedStoreConversations, setSavedStoreConversations] = useState(
    userProfileData.storeConversations ?? false
  );
  const [savedRole, setSavedRole] = useState(userProfileData.professionalRole);
  const [savedGoals, setSavedGoals] = useState(userProfileData.goals);
  const [savedDifficulty, setSavedDifficulty] = useState(
    getConfidenceScores(userProfileData, 'giving_difficult_feedback')[0]
  );
  const [savedConflict, setSavedConflict] = useState(
    getConfidenceScores(userProfileData, 'managing_team_conflicts')[0]
  );
  const [savedConversation, setSavedConversation] = useState(
    getConfidenceScores(userProfileData, 'leading_challenging_conversations')[0]
  );

  const hasFormChanged = () => {
    return (
      storeConversations !== savedStoreConversations ||
      currentRole !== savedRole ||
      JSON.stringify(primaryGoals) !== JSON.stringify(savedGoals) ||
      difficulty[0] !== savedDifficulty ||
      conflict[0] !== savedConflict ||
      conversation[0] !== savedConversation
    );
  };

  const confidenceFieldsProps = {
    difficulty,
    conflict,
    conversation,
    setDifficulty,
    setConflict,
    setConversation,
  };
  const currentRoleSelect: UserPreference = {
    label: tOptions('currentRole.label'),
    options: UserRoles(),
    value: currentRole,
    defaultValue: 'team_leader',
    onChange: (value: string) => {
      setCurrentRole(value);
    },
  };
  const primaryGoalsSelect: UserPreference<string[]> = {
    label: tOptions('primaryGoals.label'),
    options: PrimaryGoals(),
    value: primaryGoals.slice(0, 3),
    placeholder: tOptions('primaryGoals.placeholder'),
    maxSelectedDisclaimer: tOptions('primaryGoals.maxOptionsSelected'),
    onChange: (value: string[]) => {
      setPrimaryGoals(value);
    },
  };

  const handleSaveSettings = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      await UserProfileService.updateUserProfile(api, {
        fullName: userProfileData.fullName,
        storeConversations,
        professionalRole: currentRole,
        goals: primaryGoals,
        confidenceScores: [
          { confidenceArea: 'giving_difficult_feedback', score: difficulty[0] },
          { confidenceArea: 'managing_team_conflicts', score: conflict[0] },
          { confidenceArea: 'leading_challenging_conversations', score: conversation[0] },
        ],
      });
      showSuccessToast(t('saveSettingsSuccess'));

      setSavedStoreConversations(storeConversations);
      setSavedRole(currentRole);
      setSavedGoals([...primaryGoals]);
      setSavedDifficulty(difficulty[0]);
      setSavedConflict(conflict[0]);
      setSavedConversation(conversation[0]);
    } catch (error) {
      showErrorToast(error, t('saveSettingsError'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await UserProfileService.exportUserData();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'user_data_export.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showSuccessToast(t('exportSuccess'));
    } catch (error) {
      showErrorToast(error, t('exportError'));
    }
  };

  return (
    <div>
      <h1 className="text-2xl">{t('title')}</h1>

      <div className="space-y-4 flex items-center rounded-t-lg">
        <Accordion type="multiple" defaultValue={['item-1', 'item-2']}>
          {/* Privacy Controls */}
          <AccordionItem value="item-1">
            <AccordionTrigger>{t('privacyControls')}</AccordionTrigger>
            <AccordionContent>
              {/* Store Conversations */}
              <div className="flex items-center justify-between w-full px-2 gap-8">
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
              {/* Export data */}
              <div className="flex items-center justify-between w-full mt-4 px-2 gap-8">
                <div className="flex flex-col">
                  <div className="text-bw-70">{t('exportData')}</div>
                </div>
                <div className="flex items-center">
                  <Button variant="outline" className="w-full" onClick={handleExport}>
                    <Download className="w-4 h-4" />
                    <span className="hidden sm:inline">{t('export')}</span>
                  </Button>
                </div>
              </div>
              {/* Delete Account */}
              <div className="flex items-center justify-between w-full mt-4 px-2 gap-8">
                <div className="flex flex-col">
                  <div className="text-bw-70">{t('deleteAccount')}</div>
                </div>
                <DeleteUserHandler>
                  <Button variant="destructive">{t('deleteAccount')}</Button>
                </DeleteUserHandler>
              </div>
            </AccordionContent>
          </AccordionItem>
          {/* Personalization Settings */}
          <AccordionItem value="item-2">
            <AccordionTrigger>{t('personalizationSettings')}</AccordionTrigger>
            <AccordionContent>
              <UserPreferences
                className="flex flex-col gap-8 px-2"
                currentRole={currentRoleSelect}
                primaryGoals={primaryGoalsSelect}
              />
              <hr className="border-bw-20 px-2" />
              <UserConfidenceFields
                className="flex flex-col gap-8 px-2"
                {...confidenceFieldsProps}
              />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
      <Button
        size="full"
        onClick={handleSaveSettings}
        variant={isSubmitting || !hasFormChanged() ? 'disabled' : 'default'}
        disabled={isSubmitting || !hasFormChanged()}
      >
        {isSubmitting ? t('saving') : t('saveSettings')}
      </Button>
    </div>
  );
}
