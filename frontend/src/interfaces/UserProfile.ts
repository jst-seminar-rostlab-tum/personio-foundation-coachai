export interface UserProfile {
  professionalRole: string;
  goals: string[];
  storeConversations?: boolean;
  confidenceScores?: ConfidenceScore[];
}
export interface ConfidenceScore {
  confidenceArea: string;
  score: number;
}
