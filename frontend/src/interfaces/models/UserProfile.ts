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

export interface PaginatedUsersParams {
  page?: number;
  pageSize?: number;
  emailSubstring?: string;
}

export interface UserPaginationResponse {
  initialUsers: UserProfile[];
  totalCount: number;
  initialPage: number;
  pageSize: number;
}
