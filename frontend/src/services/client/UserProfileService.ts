import { UserProfile, UserProfileUpdate } from '@/interfaces/UserProfile';
import { api } from './Api';

interface KeyConcept {
  header: string;
  value: string;
}

interface UserDataExport {
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

const updateUserProfile = async (userProfile: UserProfileUpdate): Promise<UserProfile> => {
  try {
    const { data } = await api.patch<UserProfile>('/user-profile', userProfile);
    return data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

const exportUserData = async (): Promise<UserDataExport> => {
  try {
    const { data } = await api.get<UserDataExport>('/user-profile/export');
    return data;
  } catch (error) {
    console.error('Error exporting user data:', error);
    throw error;
  }
};

export const UserProfileService = {
  updateUserProfile,
  exportUserData,
};
