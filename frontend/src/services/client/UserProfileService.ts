import { UserProfile, UserProfileUpdate } from '@/interfaces/UserProfile';
import { api } from './Api';

const updateUserProfile = async (userProfile: UserProfileUpdate): Promise<UserProfile> => {
  try {
    const { data } = await api.patch<UserProfile>('/user-profile', userProfile);
    return data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

export const UserProfileService = {
  updateUserProfile,
};
