'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';

import Stepper from '@/components/common/Stepper';
import { Button } from '@/components/ui/Button';
import Checkbox from '@/components/ui/Checkbox';
import Label from '@/components/ui/Label';
import UserConfidenceFields from '@/components/common/UserConfidenceFields';

import { UserOption } from '@/interfaces/models/UserInputFields';
import { PrimaryGoals, UserRoles } from '@/lib/utils';
import { UserProfileService } from '@/services/client/UserProfileService';
import { showErrorToast } from '@/lib/toast';
import { useUser } from '@/contexts/User';
import { useOnboardingStore } from '@/store/OnboardingStore';
import { UserRadioComponent } from './UserRadioComponent';

export default function OnboardingPageComponent() {
  const t = useTranslations('Onboarding');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const userProfile = useUser();

  const onboardingSteps = ['Step1', 'Step2', 'Step3'];
  const roleQuestion: UserOption[] = UserRoles();
  const primaryGoals: UserOption[] = PrimaryGoals();

  const {
    step,
    setStep,
    role,
    setRole,
    goals,
    setGoals,
    difficulty,
    setDifficulty,
    conflict,
    setConflict,
    conversation,
    setConversation,
    reset,
  } = useOnboardingStore();

  const isValidStep = (stepIndex: number) => {
    if (stepIndex === 0) return role !== '';
    if (stepIndex === 1) return goals.length > 0;
    return true;
  };

  const handleStepChange = (stepIndex: number) => {
    if (!isValidStep(stepIndex - 1)) return;
    if (stepIndex <= step || stepIndex === step + 1) {
      setStep(stepIndex);
    }
  };

  const updateUserProfile = async () => {
    try {
      await UserProfileService.updateUserProfile({
        fullName: userProfile.fullName,
        professionalRole: role,
        goals,
        confidenceScores: [
          { confidenceArea: 'giving_difficult_feedback', score: difficulty[0] },
          { confidenceArea: 'managing_team_conflicts', score: conflict[0] },
          { confidenceArea: 'leading_challenging_conversations', score: conversation[0] },
        ],
      });
      router.push('/dashboard');
      setTimeout(reset, 2000);
    } catch (error) {
      showErrorToast(error, t('updateProfileError'));
    }
  };

  return (
    <div className="flex flex-col max-w-2xl py-5 gap-5 mr-auto ml-auto">
      <div className="flex flex-col gap-2 text-center">
        <span className="text-2xl">{t('title')}</span>
        <span className="text-base text-bw-40">{t('subtitle')}</span>
      </div>

      <Stepper
        steps={onboardingSteps}
        currentStep={step}
        onStepClick={handleStepChange}
        showAllStepNumbers={true}
        showStepLabels={false}
        currentStepValid={isValidStep(step)}
      />

      {step === 0 && (
        <UserRadioComponent
          question={t('steps.step1')}
          options={roleQuestion}
          selectedValue={role}
          onValueChange={setRole}
          labelHintAlign="vertical"
        />
      )}

      {step === 1 && (
        <>
          <div className="text-center flex flex-col justify-around min-h-20">
            <div className="text-xl">{t('steps.step2')}</div>
            <div className="text-base text-bw-40">{t('steps.step2Subtitle')}</div>
          </div>
          <div className="h-63 overflow-y-auto">
            <div className="flex flex-col gap-5">
              {primaryGoals.map((goal) => (
                <div key={goal.id} className="flex items-center gap-2">
                  <Checkbox
                    id={goal.id}
                    checked={goals.includes(goal.id)}
                    onCheckedChange={(checked) => {
                      if (checked && goals.length < 3) {
                        setGoals([...goals, goal.id]);
                      } else if (!checked) {
                        setGoals(goals.filter((g: string) => g !== goal.id));
                      }
                    }}
                  />
                  <Label htmlFor={goal.id} className="text-lg">
                    {goal.label}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {step === 2 && (
        <>
          <div className="text-xl self-center min-h-20 text-center max-w-70 flex items-center">
            {t('steps.step3')}
          </div>
          <UserConfidenceFields
            difficulty={difficulty}
            conflict={conflict}
            conversation={conversation}
            setDifficulty={setDifficulty}
            setConflict={setConflict}
            setConversation={setConversation}
          />
        </>
      )}

      <div className="flex flex-col gap-3 items-center">
        <div className={`grid w-full gap-3 ${step > 0 ? 'grid-cols-2' : 'grid-cols-1'}`}>
          {step > 0 && (
            <Button
              className="w-full"
              variant="outline"
              onClick={() => setStep(step - 1)}
              disabled={step === 0}
            >
              <ArrowLeftIcon />
              {tCommon('back')}
            </Button>
          )}
          {step === onboardingSteps.length - 1 ? (
            <Button className="w-full" onClick={updateUserProfile}>
              {tCommon('finish')}
              <ArrowRightIcon />
            </Button>
          ) : (
            <Button
              className="w-full"
              onClick={() => setStep(step + 1)}
              variant={isValidStep(step) ? 'default' : 'disabled'}
            >
              {tCommon('next')}
              <ArrowRightIcon />
            </Button>
          )}
        </div>
        <Link href="/dashboard" className="text-base text-bw-40 hover:underline hover:text-bw-60">
          {tCommon('skip')}
        </Link>
      </div>
    </div>
  );
}
