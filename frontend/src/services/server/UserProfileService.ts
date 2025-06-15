import { UserProfile } from '@/interfaces/UserProfile';
import { api } from './Api';

const getUserProfile = async (): Promise<UserProfile> => {
  try {
    const { data } = await api.get<UserProfile>(`/user-profile/profile`, {
      params: { detailed: true },
    });
    return data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

export const UserProfileService = {
  getUserProfile,
};
