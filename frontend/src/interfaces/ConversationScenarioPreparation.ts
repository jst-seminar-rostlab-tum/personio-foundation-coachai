export type KeyConcept = {
  header: string;
  value: string;
};

export type ConversationScenarioPreparation = {
  id: string;
  scenarioId: string;
  objectives: string[];
  keyConcepts: KeyConcept[];
  prepChecklist: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
};
