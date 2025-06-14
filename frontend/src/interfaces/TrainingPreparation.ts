export type KeyConcept = {
  header: string;
  value: string;
};

export type TrainingPreparation = {
  id: string;
  caseId: string;
  objectives: string[];
  keyConcepts: KeyConcept[];
  prepChecklist: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
};
