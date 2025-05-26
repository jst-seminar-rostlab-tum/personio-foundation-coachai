export interface CustomizeStepProps {
  difficulty: string;
  emotionalTone: string;
  complexity: string;
  onDifficultyChange: (difficulty: string) => void;
  onEmotionalToneChange: (emotionalTone: string) => void;
  onComplexityChange: (complexity: string) => void;
}
