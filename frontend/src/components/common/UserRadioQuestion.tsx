import React from 'react';
import Label from '@/components/ui/Label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import { UserRadioQuestion } from '@/interfaces/UserInputFields';
import { cn } from '@/lib/utils';

export const UserRadio: React.FC<UserRadioQuestion> = ({
  question,
  options,
  labelHintAlign,
  selectedValue,
  onValueChange,
}) => {
  return (
    <>
      <div className="self-center text-xl min-h-20 max-w-70 flex items-center text-center">
        {question}
      </div>
      <div className="h-63 overflow-y-auto">
        <RadioGroup value={selectedValue} onValueChange={onValueChange}>
          {options.map((option) => (
            <div className="flex gap-2.5 items-center" key={option.id}>
              <RadioGroupItem id={option.id} value={option.label}></RadioGroupItem>
              <Label
                key={option.id}
                htmlFor={option.id}
                className={cn('text-lg flex gap-0.5', {
                  'flex-col gap-0': option.labelHint && labelHintAlign === 'vertical',
                })}
              >
                {option.label}
                {option.labelHint && (
                  <span className="text-base text-bw-40">{option.labelHint}</span>
                )}
              </Label>
            </div>
          ))}
        </RadioGroup>
      </div>
    </>
  );
};
