export interface StepperProps {
  steps: string[];
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  className?: string;
  showAllStepNumbers?: boolean;
  showStepLabels?: boolean;
}
