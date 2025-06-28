export interface UserProfile {
  fullName: string;
  email: string;
  phoneNumber: string;
  professionalRole: string;
  goals: string[];
  accountRole: AccountRole;
  storeConversations?: boolean;
  confidenceScores?: ConfidenceScore[];
}

export type UserProfileUpdate = Omit<UserProfile, 'email' | 'phoneNumber' | 'accountRole'>;

export interface ConfidenceScore {
  confidenceArea: string;
  score: number;
}

export enum AccountRole {
  user = 'user',
  admin = 'admin',
}

export interface KeyConcept {
  header: string;
  value: string;
}
