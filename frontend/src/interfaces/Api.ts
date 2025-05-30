export interface UserProfileCreate {
  full_name: string;
  email: string;
  phone_number: string;
  password: string;
  preferred_language: string;
  role_id?: string;
  experience_id?: string;
  preferred_learning_style: string;
  preferred_session_length: string;
}

export interface SignInCredentials {
  email: string;
  password: string;
}
