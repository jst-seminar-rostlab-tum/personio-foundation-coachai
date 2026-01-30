import { ConversationScenario } from './ConversationScenario';

/**
 * User profile data for the authenticated user.
 */
export interface UserProfile {
  userId: string;
  fullName: string;
  email: string;
  phoneNumber: string;
  organizationName?: string;
  professionalRole: string;
  goals: string[];
  accountRole: AccountRole;
  storeConversations?: boolean;
  confidenceScores?: ConfidenceScore[];
  scenarioAdvice: ScenarioAdvice;
  sessionsCreatedToday?: number;
  dailySessionLimit?: number;
}

/**
 * Payload for updating a user profile.
 */
export type UserProfileUpdate = Omit<
  UserProfile,
  'userId' | 'email' | 'phoneNumber' | 'accountRole' | 'scenarioAdvice'
>;

/**
 * Confidence score entry for a specific area.
 */
export interface ConfidenceScore {
  confidenceArea: string;
  score: number;
}

/**
 * Account roles for user authorization.
 */
export enum AccountRole {
  user = 'user',
  admin = 'admin',
}

/**
 * Paginated response for user lists.
 */
export interface UserPaginationResponse {
  page: number;
  totalPages: number;
  totalUsers: number;
  users: UserProfile[];
}

/**
 * Scenario advice and mascot guidance for the user.
 */
export interface ScenarioAdvice {
  scenario: ConversationScenario;
  mascotSpeech: string;
}

/**
 * Sort direction options.
 */
export enum SortOption {
  NONE = 'none',
  ASC = 'ASC',
  DESC = 'DESC',
}

/**
 * Session limit filter options.
 */
export enum SessionLimitType {
  ALL = 'all',
  DEFAULT = 'DEFAULT',
  INDIVIDUAL = 'INDIVIDUAL',
}
