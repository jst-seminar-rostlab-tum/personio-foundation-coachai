'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import React, { use, useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import Switch from '@/components/ui/Switch';
import Input from '@/components/ui/Input';
import Checkbox from '@/components/ui/Checkbox';
import UserConfidenceFields from '@/components/common/UserConfidenceFields';
import { DeleteUserHandler } from '@/components/common/DeleteUserHandler';
import { UserProfileService } from '@/services/UserProfileService';
import { UserPreference } from '@/interfaces/models/UserInputFields';
import { UserRoles } from '@/lib/constants/userRoles';
import { PrimaryGoals } from '@/lib/constants/primaryGoals';
import { UserProfile } from '@/interfaces/models/UserProfile';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { UpdateEmailHandler } from '@/components/common/UpdateEmailHandler';
import { Mail } from 'lucide-react';
import UserPreferences from './UserPreferences';
import { ExportUserHandler } from './ExportUserHandler';

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
  const tCommon = useTranslations('Common');
  const userProfileData = use(userProfile);
  const router = useRouter();
  const [storeConversations, setStoreConversations] = useState(
    userProfileData.storeConversations ?? false
  );
  const [organizationName, setOrganizationName] = useState(userProfileData.organizationName || '');
  const [isNonprofit, setIsNonprofit] = useState(userProfileData.isNonprofit || false);
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
  const [savedOrganizationName, setSavedOrganizationName] = useState(
    userProfileData.organizationName || ''
  );
  const [savedIsNonprofit, setSavedIsNonprofit] = useState(userProfileData.isNonprofit || false);
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
  const searchParams = useSearchParams();

  useEffect(() => {
    const updateEmailError = searchParams.get('updateEmailError');
    if (updateEmailError) {
      showErrorToast(updateEmailError, `${t('updateEmailError')}: ${updateEmailError}`);
    }
    const emailUpdatedSuccess = searchParams.get('emailUpdatedSuccess');
    if (emailUpdatedSuccess) {
      showSuccessToast(t('emailUpdatedSuccess'));
    }
    // eslint-disable-next-line
  }, [searchParams, t]);

  const hasFormChanged = () => {
    return (
      storeConversations !== savedStoreConversations ||
      organizationName !== savedOrganizationName ||
      isNonprofit !== savedIsNonprofit ||
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
    label: t('currentRole'),
    options: UserRoles(),
    value: currentRole,
    defaultValue: 'team_leader',
    onChange: (value: string) => {
      setCurrentRole(value);
    },
  };
  const primaryGoalsSelect: UserPreference<string[]> = {
    label: t('primaryGoals.label'),
    options: PrimaryGoals(),
    value: primaryGoals.slice(0, 3),
    placeholder: t('primaryGoals.placeholder'),
    maxSelectedDisclaimer: t('primaryGoals.maxOptionsSelected'),
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
        organizationName,
        isNonprofit,
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
      setSavedOrganizationName(organizationName);
      setSavedIsNonprofit(isNonprofit);
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

  return (
    <div>
      <div className="flex flex-col gap-8">
        <h1 className="text-2xl">{tCommon('settings')}</h1>

        <div className="space-y-4 flex items-center rounded-t-lg">
          <Accordion type="multiple" defaultValue={['item-1', 'item-2', 'item-3']}>
            {/* Privacy Controls */}
            <AccordionItem value="item-1">
              <AccordionTrigger>{t('privacyControls')}</AccordionTrigger>
              <AccordionContent>
                {/* Store Conversations */}
                <div className="flex items-center justify-between w-full px-2 gap-8">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('storeAudioTranscripts')}</div>
                    <div className="text-bw-70">
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
                    <ExportUserHandler />
                  </div>
                </div>
                <div className="flex items-center justify-between w-full mt-4 px-2 gap-8">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{t('updateEmail')}</div>
                  </div>
                  <div className="flex items-center">
                    <UpdateEmailHandler>
                      <Button variant="default" className="w-full">
                        <Mail className="w-4 h-4" />
                        <span className="hidden sm:inline">{t('updateEmail')}</span>
                      </Button>
                    </UpdateEmailHandler>
                  </div>
                </div>
                {/* Delete Account */}
                <div className="flex items-center justify-between w-full mt-4 px-2 gap-8">
                  <div className="flex flex-col">
                    <div className="text-bw-70">{tCommon('deleteAccount')}</div>
                  </div>
                  <DeleteUserHandler
                    onDeleteSuccess={() => {
                      router.push('/');
                    }}
                  />
                </div>
              </AccordionContent>
            </AccordionItem>
            {/* Organization Settings */}
            <AccordionItem value="item-2">
              <AccordionTrigger>{t('organizationSettings')}</AccordionTrigger>
              <AccordionContent>
                <div className="flex flex-col gap-6 px-2">
                  {/* Organization Name */}
                  <div className="flex flex-col gap-2">
                    <label className="text-base text-bw-70">{t('organizationName')}</label>
                    <Input
                      value={organizationName}
                      onChange={(e) => setOrganizationName(e.target.value)}
                      placeholder={t('organizationNamePlaceholder')}
                      className="w-full"
                    />
                  </div>
                  {/* Nonprofit Status */}
                  <div className="flex items-start gap-3">
                    <Checkbox checked={isNonprofit} onClick={() => setIsNonprofit(!isNonprofit)} />
                    <label
                      className="text-sm text-bw-70 cursor-pointer"
                      onClick={() => setIsNonprofit(!isNonprofit)}
                    >
                      {t('nonprofitStatus')}
                    </label>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
            {/* Personalization Settings */}
            <AccordionItem value="item-3">
              <AccordionTrigger>{t('personalizationSettings')}</AccordionTrigger>
              <AccordionContent>
                <UserPreferences
                  className="flex flex-col gap-8 px-2"
                  currentRole={currentRoleSelect}
                  primaryGoals={primaryGoalsSelect}
                />
                <hr className="border-bw-40 px-2" />
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
          {isSubmitting ? tCommon('saving') : t('saveSettings')}
        </Button>
      </div>
    </div>
  );
}
