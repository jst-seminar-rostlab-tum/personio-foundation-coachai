'use client';

import Stepper from '@/components/ui/stepper';
import React from 'react';
import { Button } from '@/components/ui/button';
import UserPreferences from '@/components/layout/UserPreferences';
import { userPreferences } from '@/configs/UserPreferences.config';
import UserConfidenceFields from '@/components/layout/UserConfidenceFields';
import { confidenceFields } from '@/configs/UserConfidenceFields.config';
import { UserOption } from '@/interfaces/UserInputFields';
import Checkbox from '@/components/ui/checkbox';
import Label from '@/components/ui/label';
import { UserRadio } from '@/components/layout/UserRadioQuestion';

export default function OnboardingPage() {
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
    { id: 'g6', label: 'Communicating organizatorial change' },
    { id: 'g7', label: 'Develop emotional intelligence' },
    { id: 'g8', label: 'Building inclusive teams' },
    { id: 'g9', label: 'Negotiation skills' },
    { id: 'g10', label: 'Coaching & Mentoring' },
  ];

  const onboardingSteps = ['Step1', 'Step2', 'Step3', 'Step4', 'Step5'];
  const [currentOnboardingStep, setCurrentOnboardingStep] = React.useState(0);
  const [selectedRole, setSelectedRole] = React.useState<string>('');
  const [selectedLeadership, setSelectedLeadership] = React.useState<string>('');
  const [selectedGoals, setSelectedGoals] = React.useState<string[]>([]);

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
    <div>
      <div className="flex flex-col w-fit gap-5 m-auto">
        <div className="flex flex-col gap-2 text-center">
          <span className="text-2xl">Personalize Your Experience</span>
          <span className="text-base text-bw-40">
            Tailor your leadership training to your needs
          </span>
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
            question="What is your primary role?"
            options={roleQuestion}
            selectedValue={selectedRole}
            onValueChange={setSelectedRole}
            labelHintAlign="vertical"
          />
        )}
        {currentOnboardingStep === 1 && (
          <UserRadio
            question="How much leadership experience do you have?"
            options={leadershipQuestion}
            selectedValue={selectedLeadership}
            onValueChange={setSelectedLeadership}
          />
        )}

        {currentOnboardingStep === 2 && (
          <>
            <div className="self-center flex flex-col justify-around min-h-20">
              <div className="text-xl">What are your primary goals?</div>
              <div className="text-base text-bw-40">
                Select up to 3 areas youd like to focus on.
              </div>
            </div>
            <div className="flex flex-col gap-5">
              {primaryGoals.map((goal) => (
                <div key={goal.id} className="flex items-center gap-2">
                  <Checkbox
                    id={goal.id}
                    checked={selectedGoals.includes(goal.id)}
                    onCheckedChange={(checked) => {
                      if (checked) {
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
              Rate Your Confidence in These Areas
            </div>
            <UserPreferences preferences={userPreferences} />
          </>
        )}

        {currentOnboardingStep === 4 && (
          <>
            <div className="text-xl self-center min-h-20 text-center max-w-70 flex items-center">
              Your Preferences
            </div>

            <UserConfidenceFields fields={confidenceFields} />
          </>
        )}

        <div className="flex justify-center gap-3">
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
