'use client';

import Stepper from '@/components/ui/stepper';
import React from 'react';
import { Button } from '@/components/ui/button';
import UserPreferences from '@/components/layout/UserPreferences';
import { useUserPreferences } from '@/configs/UserPreferences.config';
import UserConfidenceFields from '@/components/layout/UserConfidenceFields';
import { useUserConfidenceFields } from '@/configs/UserConfidenceFields.config';

export default function OnboardingPage() {
  const [currentOnboardingStep, setCurrentOnboardingStep] = React.useState(0);

  const onboardingSteps = ['Step1', 'Step2', 'Step3', 'Step4', 'Step5'];
  const userPreferences = useUserPreferences();
  const userConfidenceFields = useUserConfidenceFields();

  const handleStepChange = (stepIndex: number) => {
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
    <div className="flex flex-col items-center p-8 space-y-8">
      <h1 className="text-2xl font-bold text-center mb-8">Onboarding Process</h1>

      <Stepper
        steps={onboardingSteps}
        currentStep={currentOnboardingStep}
        onStepClick={handleStepChange}
        showAllStepNumbers={true}
        showStepLabels={true}
        className="mb-8 md:w-1/2"
      />

      <div className="text-center text-lg">
        <p>
          You are currently on:{' '}
          <span className="font-semibold text-blue-600">
            {onboardingSteps[currentOnboardingStep]}
          </span>
        </p>
        {currentOnboardingStep === 0 && (
          <UserPreferences className="md:w-1/2" preferences={userPreferences} />
        )}
        {currentOnboardingStep === 1 && (
          <UserConfidenceFields className="md:w-1/2" fields={userConfidenceFields} />
        )}

        <div className="flex justify-center space-x-4 mt-8">
          <Button onClick={goToPreviousStep} disabled={currentOnboardingStep === 0}>
            Previous
          </Button>
          <Button
            onClick={goToNextStep}
            disabled={currentOnboardingStep === onboardingSteps.length - 1}
          >
            {currentOnboardingStep === onboardingSteps.length - 1 ? 'Finish' : 'Next'}
          </Button>
        </div>
      </div>
    </div>
  );
}
