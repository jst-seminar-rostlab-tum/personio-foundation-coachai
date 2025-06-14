export interface UserProfile {
  professionalRole: string;
  storeConversations: boolean;
  goals: string[];
  confidenceScores?: ConfidenceScore[];
}
export interface ConfidenceScore {
  confidenceArea: string;
  score: number;
}
