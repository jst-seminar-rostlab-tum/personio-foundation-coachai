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

const deleteUser = async (deleteUserId?: string) => {
  try {
    const url = `/user-profile${deleteUserId ? `?delete_user_id=${deleteUserId}` : ''}`;
    const { data } = await api.delete(url);
    return data;
  } catch (error) {
    console.error('Error deleting user ', error);
    throw error;
  }
};

interface PaginatedUsersParams {
  page?: number;
  pageSize?: number;
  limit?: number;
  emailSubstring?: string;
}

const getPaginatedUsers = async (params: PaginatedUsersParams = {}) => {
  const { page = 1, pageSize = 10, limit, emailSubstring } = params;
  try {
    const { data } = await api.get('/user-profile', {
      params: {
        page,
        page_size: pageSize || limit,
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
  updateUserProfile,
  exportUserData,
  deleteUser,
  getPaginatedUsers,
};
