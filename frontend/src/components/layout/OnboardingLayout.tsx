'use client';

import Stepper from '@/components/common/Stepper';
import React from 'react';
import { Button } from '@/components/ui/Button';
import UserPreferences from '@/components/common/UserPreferences';
import { userPreferences } from '@/configs/UserPreferences.config';
import UserConfidenceFields from '@/components/common/UserConfidenceFields';
import { confidenceFields } from '@/configs/UserConfidenceFields.config';
import { UserOption } from '@/interfaces/UserInputFields';
import Checkbox from '@/components/ui/Checkbox';
import Label from '@/components/ui/Label';
import { UserRadio } from '@/components/layout/UserRadioQuestion';
import { useTranslations } from 'next-intl';
import { ArrowLeftIcon, ArrowRightIcon } from 'lucide-react';
import Link from 'next/link';

export default function OnboardingLayout() {
  const roleQuestion: UserOption[] = [
    {
      id: 'r1',
      label: 'HR Professional',
      labelHint: 'I work in human resources or people operations',
    },
    {
      id: 'r2',
      label: 'Team Leader',
      labelHint: 'I manage a team or department',
    },
    {
      id: 'r3',
      label: 'Executive',
      labelHint: `I'm a director, VP, or C-level executive`,
    },
    {
      id: 'r4',
      label: 'Other',
      labelHint: 'None of them above',
    },
  ];

  const leadershipQuestion: UserOption[] = [
    { id: 'e1', label: 'Beginner', labelHint: '(<1 year)' },
    { id: 'e2', label: 'Intermediate', labelHint: '(1-3 years)' },
    { id: 'e3', label: 'Skilled', labelHint: '(3-5 years)' },
    { id: 'e4', label: 'Advanced', labelHint: '(5-10 years)' },
    { id: 'e5', label: 'Expert', labelHint: '(>10 years)' },
  ];

  const primaryGoals: UserOption[] = [
    { id: 'g1', label: 'Giving constructive feedback' },
    { id: 'g2', label: 'Managing team conflicts' },
    { id: 'g3', label: 'Performance reviews' },
    { id: 'g4', label: 'Motivating team members' },
    { id: 'g5', label: 'Leading difficult conversations' },
  ];

  const onboardingSteps = ['Step1', 'Step2', 'Step3', 'Step4', 'Step5'];
  const [currentOnboardingStep, setCurrentOnboardingStep] = React.useState(0);
  const [selectedRole, setSelectedRole] = React.useState<string>('');
  const [selectedLeadership, setSelectedLeadership] = React.useState<string>('');
  const [selectedGoals, setSelectedGoals] = React.useState<string[]>([]);
  const t = useTranslations('Onboarding');

  const isValidStep = (stepIndex: number) => {
    if (stepIndex === 0) return selectedRole !== '';
    if (stepIndex === 1) return selectedLeadership !== '';
    if (stepIndex === 2) return selectedGoals.length > 0;
    return true;
  };
  const handleStepChange = (stepIndex: number) => {
    if (!isValidStep(stepIndex - 1)) {
      return;
    }
    if (stepIndex <= currentOnboardingStep || stepIndex === currentOnboardingStep + 1) {
      setCurrentOnboardingStep(stepIndex);
    }
  };

  const goToNextStep = () => {
    setCurrentOnboardingStep((prev) => Math.min(prev + 1, onboardingSteps.length - 1));
  };

  const goToPreviousStep = () => {
    setCurrentOnboardingStep((prev) => Math.max(prev - 1, 0));
  };

  return (
    <div className="flex flex-col w-fit py-5 gap-5 mr-auto ml-auto">
      <div className="flex flex-col gap-2 text-center">
        <span className="text-2xl">{t('title')}</span>
        <span className="text-base text-bw-40">{t('subtitle')}</span>
      </div>
      <Stepper
        steps={onboardingSteps}
        currentStep={currentOnboardingStep}
        onStepClick={handleStepChange}
        showAllStepNumbers={true}
        showStepLabels={false}
      />

      {currentOnboardingStep === 0 && (
        <UserRadio
          question={t('steps.step1')}
          options={roleQuestion}
          selectedValue={selectedRole}
          onValueChange={setSelectedRole}
          labelHintAlign="vertical"
        />
      )}
      {currentOnboardingStep === 1 && (
        <UserRadio
          question={t('steps.step2')}
          options={leadershipQuestion}
          selectedValue={selectedLeadership}
          onValueChange={setSelectedLeadership}
        />
      )}

      {currentOnboardingStep === 2 && (
        <>
          <div className="text-center flex flex-col justify-around min-h-20">
            <div className="text-xl">{t('steps.step3')}</div>
            <div className="text-base text-bw-40">{t('steps.step3Subtitle')}</div>
          </div>
          <div className="flex flex-col gap-5">
            {primaryGoals.map((goal) => (
              <div key={goal.id} className="flex items-center gap-2">
                <Checkbox
                  id={goal.id}
                  checked={selectedGoals.includes(goal.id)}
                  onCheckedChange={(checked) => {
                    if (checked && selectedGoals.length < 3) {
                      setSelectedGoals((prev) => [...prev, goal.id]);
                    } else {
                      setSelectedGoals((prev) => prev.filter((g) => g !== goal.id));
                    }
                  }}
                />
                <Label htmlFor={goal.id} className="text-lg">
                  {goal.label}
                </Label>
              </div>
            ))}
          </div>
        </>
      )}

      {currentOnboardingStep === 3 && (
        <>
          <div className="text-xl self-center min-h-20 text-center max-w-70 flex items-center">
            {t('steps.step4')}
          </div>
          <UserConfidenceFields fields={confidenceFields} />
        </>
      )}

      {currentOnboardingStep === 4 && (
        <>
          <div className="text-xl self-center min-h-20 text-center max-w-70 flex items-center">
            {t('steps.step5')}
          </div>
          <UserPreferences preferences={userPreferences} />
        </>
      )}
      <div className="flex flex-col gap-3 items-center">
        <div
          className={`grid w-full gap-3 ${currentOnboardingStep > 0 ? 'grid-cols-2' : 'grid-cols-1'}`}
        >
          {currentOnboardingStep > 0 && (
            <Button
              className="w-full"
              variant="outline"
              onClick={goToPreviousStep}
              disabled={currentOnboardingStep === 0}
            >
              <ArrowLeftIcon />
              {t('navigation.back')}
            </Button>
          )}

          {currentOnboardingStep === onboardingSteps.length - 1 ? (
            <Link href="/dashboard">
              <Button className="w-full">
                {t('navigation.finish')}
                <ArrowRightIcon />
              </Button>
            </Link>
          ) : (
            <Button
              className="w-full"
              onClick={goToNextStep}
              variant={isValidStep(currentOnboardingStep) ? 'default' : 'disabled'}
            >
              {t('navigation.next')}
              <ArrowRightIcon />
            </Button>
          )}
        </div>

        <Link href={'/dashboard'} className="text-base text-bw-40">
          {t('navigation.skip')}
        </Link>
      </div>
    </div>
  );
}
