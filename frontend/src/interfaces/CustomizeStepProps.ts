import { Persona } from './Persona';

export interface CustomizeStepProps {
  difficulty: string;
  complexity: string;
  selectedPersona: string;
  onDifficultyChange: (difficulty: string) => void;
  onComplexityChange: (complexity: string) => void;
  onPersonaSelect: (persona: Persona) => void;
}
