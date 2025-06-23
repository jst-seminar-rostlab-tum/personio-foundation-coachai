import { UserProfile, UserProfileUpdate, UserDataExport } from '@/interfaces/UserProfile';
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
