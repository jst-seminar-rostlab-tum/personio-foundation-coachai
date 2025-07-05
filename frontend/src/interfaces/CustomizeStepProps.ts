import { Persona } from './Persona';

export interface CustomizeStepProps {
  difficulty: string;
  selectedPersona: string;
  onDifficultyChange: (difficulty: string) => void;
  onPersonaSelect: (persona: Persona) => void;
}
