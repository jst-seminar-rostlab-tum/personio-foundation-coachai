export interface UserProfileCreate {
  email: string;
  full_name: string;
  phone_number: string;
  password: string;
  preferred_language?: string;
  role_id?: string;
  experience_id?: string;
  preferred_learning_style_id?: string;
  preferred_session_length_id?: string;
  store_conversations?: boolean;
}
