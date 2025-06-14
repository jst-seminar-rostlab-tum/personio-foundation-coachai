import { UserProfile } from '@/interfaces/UserProfile';
import { api } from './Api';

const getUserProfile = async (userId: string): Promise<UserProfile> => {
  try {
    const { data } = await api.get<UserProfile>(`/user-profile/${userId}`);
    return data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

const updateUserProfile = async (userProfile: UserProfile): Promise<UserProfile> => {
  try {
    const { data } = await api.put<UserProfile>('/user-profile', userProfile);
    return data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

export const UserProfileService = {
  getUserProfile,
  updateUserProfile,
};
