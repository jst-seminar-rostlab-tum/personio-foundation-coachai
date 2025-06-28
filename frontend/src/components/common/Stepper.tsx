'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { CheckIcon } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface StepperProps {
  steps: string[];
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  className?: string;
  showAllStepNumbers?: boolean;
  showStepLabels?: boolean;
  currentStepValid?: boolean;
}

const Stepper: React.FC<StepperProps> = ({
  steps,
  currentStep,
  onStepClick,
  className,
  showAllStepNumbers,
  showStepLabels,
  currentStepValid,
}) => {
  return (
    <div className={cn('flex items-start justify-center w-full', className)}>
      {steps.map((step, index) => (
        <React.Fragment key={step}>
          <div className="flex flex-col gap-2 relative">
            <Button
              className={cn(
                'size-10 rounded-full transition-colors duration-200 flex items-center justify-center text-white p-0',
                {
                  'bg-marigold-50': index <= currentStep,
                  'border-1 border-solid border-bw-20 bg-bw-10 hover:bg-bw-30 text-bw-40':
                    index > currentStep,
                }
              )}
              onClick={() => onStepClick && onStepClick(index)}
              disabled={index > currentStep + 1 || !currentStepValid}
            >
              {index < currentStep ? (
                <CheckIcon className="size-5" strokeWidth={3} />
              ) : (
                (index === currentStep || showAllStepNumbers) && (
                  <span className="font-semibold text-xl">{index + 1}</span>
                )
              )}
            </Button>
            {showStepLabels && (
              <span
                className={cn(
                  'text-base text-bw-40 absolute left-1/2 -translate-x-1/2 top-full mt-4 whitespace-nowrap',
                  {
                    'text-marigold-50': index <= currentStep,
                  }
                )}
              >
                {step}
              </span>
            )}
          </div>
          {index < steps.length - 1 && (
            <div
              className={cn('h-1 bg-bw-20 transition-colors duration-200 flex-1 min-w-4 mt-4.5', {
                'bg-marigold-50': index < currentStep,
              })}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

export default Stepper;
