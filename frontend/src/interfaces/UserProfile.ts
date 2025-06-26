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

export interface KeyConcept {
  header: string;
  value: string;
}

export interface UserDataExport {
  profile: {
    user_id: string;
    full_name: string;
    email: string;
    phone_number: string | null;
    preferred_language_code: string;
    account_role: string;
    professional_role: string;
    experience: string;
    preferred_learning_style: string;
    updated_at: string | null;
    store_conversations: boolean;
    total_sessions: number;
    training_time: number;
    current_streak_days: number;
    average_score: number;
    goals_achieved: number;
  };
  goals: Array<{
    goal: string;
    updated_at: string | null;
  }>;
  confidence_scores: Array<{
    confidence_area: string;
    score: number;
    updated_at: string | null;
  }>;
  scenarios: Array<{
    id: string;
    category_id: string;
    custom_category_label: string | null;
    language_code: string;
    context: string;
    goal: string;
    other_party: string;
    difficulty_level: string;
    tone: string;
    complexity: string;
    status: string;
    created_at: string | null;
    updated_at: string | null;
  }>;
  scenario_preparations: Array<{
    id: string;
    scenario_id: string;
    objectives: string[];
    key_concepts: KeyConcept[];
    prep_checklist: string[];
    status: string;
    created_at: string | null;
    updated_at: string | null;
  }>;
  sessions: Array<{
    id: string;
    scenario_id: string;
    scheduled_at: string | null;
    started_at: string | null;
    ended_at: string | null;
    ai_persona: string;
    status: string;
    created_at: string | null;
    updated_at: string | null;
  }>;
  session_turns: Array<{
    id: string;
    session_id: string;
    speaker: string;
    start_offset_ms: number;
    end_offset_ms: number;
    text: string;
    audio_uri: string | null;
    ai_emotion: string | null;
    created_at: string | null;
  }>;
  session_feedback: Array<{
    id: string;
    session_id: string;
    scores: Record<string, number>;
    tone_analysis: Record<string, unknown>;
    overall_score: number;
    transcript_uri: string | null;
    speak_time_percent: number;
    questions_asked: number;
    session_length_s: number;
    goals_achieved: number;
    example_positive: string | null;
    example_negative: string | null;
    recommendations: string[] | null;
    status: string;
    created_at: string | null;
    updated_at: string | null;
  }>;
  reviews: Array<{
    id: string;
    user_id: string;
    session_id: string | null;
    rating: number;
    comment: string | null;
    created_at: string | null;
  }>;
}
