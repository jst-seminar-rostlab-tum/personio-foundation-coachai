import React from 'react';
import { cn } from '@/lib/utils';
import { CheckIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { StepperProps } from '@/interfaces/Props';

const Stepper: React.FC<StepperProps> = ({ steps, currentStep, onStepClick, className }) => {
  return (
    <div className={cn('flex items-center justify-center w-full', className)}>
      {steps.map((step, index) => (
        <React.Fragment key={step}>
          <Button
            variant={index <= currentStep ? 'default' : 'disabled'}
            className={cn(
              'size-10 rounded-full transition-colors duration-200 flex items-center justify-center text-white p-0',
              {
                'bg-marigold-50': index <= currentStep,
                'border-1 border-solid border-bw-20': index > currentStep,
              }
            )}
            onClick={() => onStepClick(index)}
            disabled={index > currentStep + 1}
          >
            {index < currentStep ? (
              <CheckIcon className="size-5" strokeWidth={3} />
            ) : (
              index === currentStep && <span className="font-semibold text-icon">{index + 1}</span>
            )}
          </Button>

          {index < steps.length - 1 && (
            <div
              className={cn('h-1 bg-bw-20 transition-colors duration-200 flex-1 min-w-4', {
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
