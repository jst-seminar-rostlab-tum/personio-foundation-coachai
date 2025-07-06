import { UserProfile, UserProfileUpdate } from '@/interfaces/models/UserProfile';
import { AxiosInstance } from 'axios';

const getUserProfile = async (api: AxiosInstance): Promise<UserProfile> => {
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

const getUserStats = async (api: AxiosInstance) => {
  try {
    const { data } = await api.get(`/user-profile/stats`);
    return data;
  } catch (error) {
    console.error('Error getting user stats:', error);
    throw error;
  }
};

const updateUserProfile = async (
  api: AxiosInstance,
  userProfile: UserProfileUpdate
): Promise<UserProfile> => {
  try {
    const { data } = await api.patch<UserProfile>('/user-profile', userProfile);
    return data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

const exportUserData = async (api: AxiosInstance) => {
  try {
    const { data } = await api.get('/user-profile/export');
    return data;
  } catch (error) {
    console.error('Error exporting user data:', error);
    throw error;
  }
};

const deleteUser = async (api: AxiosInstance, deleteUserId?: string) => {
  try {
    const url = `/user-profile${deleteUserId ? `?delete_user_id=${deleteUserId}` : ''}`;
    const { data } = await api.delete(url);
    return data;
  } catch (error) {
    console.error('Error deleting user ', error);
    throw error;
  }
};

const getPaginatedUsers = async (
  api: AxiosInstance,
  page: number,
  limit: number,
  emailSubstring?: string
) => {
  try {
    const { data } = await api.get('/user-profile', {
      params: {
        page,
        limit,
        email_substring: emailSubstring,
      },
    });
    return data;
  } catch (error) {
    console.error('Error getting users:', error);
    throw error;
  }
};

export const UserProfileService = {
  getUserProfile,
  getUserStats,
  updateUserProfile,
  exportUserData,
  deleteUser,
  getPaginatedUsers,
};
