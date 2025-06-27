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

export enum ConfidenceArea {
  giving_difficult_feedback = 'giving_difficult_feedback',
  managing_team_conflicts = 'managing_team_conflicts',
  leading_challenging_conversations = 'leading_challenging_conversations',
}

export enum LanguageCode {
  en = 'en',
  de = 'de',
}

export enum AccountRole {
  user = 'user',
  admin = 'admin',
}

export enum ProfessionalRole {
  hr_professional = 'hr_professional',
  team_leader = 'team_leader',
  executive = 'executive',
  other = 'other',
}

export enum Experience {
  beginner = 'beginner',
  intermediate = 'intermediate',
  skilled = 'skilled',
  advanced = 'advanced',
  expert = 'expert',
}

export enum PreferredLearningStyle {
  visual = 'visual',
  auditory = 'auditory',
  kinesthetic = 'kinesthetic',
}

export enum Goal {
  giving_constructive_feedback = 'giving_constructive_feedback',
  managing_team_conflicts = 'managing_team_conflicts',
  performance_reviews = 'performance_reviews',
  motivating_team_members = 'motivating_team_members',
  leading_difficult_conversations = 'leading_difficult_conversations',
  communicating_organizational_change = 'communicating_organizational_change',
  develop_emotional_intelligence = 'develop_emotional_intelligence',
  building_inclusive_teams = 'building_inclusive_teams',
  negotiation_skills = 'negotiation_skills',
  coaching_mentoring = 'coaching_mentoring',
}
