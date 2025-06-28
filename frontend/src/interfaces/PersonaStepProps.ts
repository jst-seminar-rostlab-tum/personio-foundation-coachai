import { Persona } from './Persona';

export interface PersonaStepProps {
  selectedPersona: string;
  onPersonaSelect: (persona: Persona) => void;
  personas: Persona[];
}
