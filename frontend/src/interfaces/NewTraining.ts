export interface FormState {
  category: string;
  customCategory: string;
  party: {
    type: string;
    otherName?: string;
  };
  context: string;
  goal: string;
  difficulty: string;
  emotionalTone: string;
  complexity: string;
}

export interface NewTrainingDTO {
  userId: string;
  categoryId: string;
  customCategoryLabel: string;
  context: string;
  goal: string;
  otherParty: string;
  difficultyLevel: string;
  userId: '3fa85f64-5717-4562-b3fc-2c963f66afa6';
  categoryId: '3fa85f64-5717-4562-b3fc-2c963f66afa6';
  customCategoryLabel: 'string';
  context: 'string';
  goal: 'string';
  otherParty: 'string';
  difficultyLevel: 'easy';
  tone: 'string';
  complexity: 'string';
  languageCode: 'en';
  status: 'draft';
}
