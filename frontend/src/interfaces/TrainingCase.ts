export interface TrainingCase {
  category_id: string;
  custom_category_label: string;
  title: string;
  context: string;
  goal: string;
  other_party: string;
  difficulty: string;
  complexity: string;
  tone: string;
}

export interface TrainingCaseResponse {
  id: string;
  user_id: string;
  scenario_template_id: string;
  context: string;
  goal: string;
  other_party: string;
  difficulty: string;
  tone: string;
  complexity: string;
  status: string;
  created_at: string;
  updated_at: string;
}
