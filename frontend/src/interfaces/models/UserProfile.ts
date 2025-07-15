import { ConversationScenario } from './ConversationScenario';

export interface UserProfile {
  userId: string;
  fullName: string;
  email: string;
  phoneNumber: string;
  professionalRole: string;
  goals: string[];
  accountRole: AccountRole;
  storeConversations?: boolean;
  confidenceScores?: ConfidenceScore[];
  scenarioAdvice: ScenarioAdvice;
}

export type UserProfileUpdate = Omit<
  UserProfile,
  'userId' | 'email' | 'phoneNumber' | 'accountRole'
>;

export interface ConfidenceScore {
  confidenceArea: string;
  score: number;
}

export enum AccountRole {
  user = 'user',
  admin = 'admin',
}

export interface UserPaginationResponse {
  page: number;
  limit: number;
  totalPages: number;
  totalUsers: number;
  users: UserProfile[];
}

export interface ScenarioAdvice {
  scenario: ConversationScenario;
  mascotSpeech: string;
}
