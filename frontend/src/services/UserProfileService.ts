import { UserProfile, UserProfileUpdate } from '@/interfaces/models/UserProfile';
import { AxiosInstance } from 'axios';

const getUserProfile = async (api: AxiosInstance) => {
  try {
    const { data } = await api.get<UserProfile>(`/user-profiles/profile`, {
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
    const { data } = await api.get(`/user-profiles/stats`);
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
    const { data } = await api.patch<UserProfile>('/user-profiles', userProfile);
    return data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
};

const exportUserData = async (api: AxiosInstance) => {
  try {
    const response = await api.get('/user-profiles/export', { responseType: 'blob' });
    return response.data;
  } catch (error) {
    console.error('Error exporting user data:', error);
    throw error;
  }
};

const deleteUser = async (api: AxiosInstance, deleteUserId?: string) => {
  try {
    const url = `/user-profiles${deleteUserId ? `?delete_user_id=${deleteUserId}` : ''}`;
    const { data } = await api.delete(url);
    return data;
  } catch (error) {
    console.error('Error deleting user ', error);
    throw error;
  }
};

const deleteUnconfirmedUser = async (api: AxiosInstance, email: string) => {
  try {
    const { data } = await api.post('/auth/delete-unconfirmed', { email });
    return data;
  } catch (error) {
    console.error('Error deleting unconfirmed user:', error);
    throw error;
  }
};

const checkUnique = async (api: AxiosInstance, email: string, phone: string) => {
  try {
    const { data } = await api.post('/auth/check-unique', { email, phone });
    return data;
  } catch (error) {
    console.error('Error checking unique email/phone:', error);
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
    const { data } = await api.get('/user-profiles', {
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
  deleteUnconfirmedUser,
  checkUnique,
  getPaginatedUsers,
};
