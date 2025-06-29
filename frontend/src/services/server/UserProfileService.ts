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

const getUserStats = async () => {
  try {
    const { data } = await api.get(`/user-profile/stats`);
    return data;
  } catch (error) {
    console.error('Error getting user stats:', error);
    throw error;
  }
};

interface PaginatedUsersParams {
  page?: number;
  pageSize?: number;
  limit?: number;
  emailSubstring?: string;
}

const getPaginatedUsers = async (
  apiInstance = api,
  { page = 1, pageSize = 10, limit, emailSubstring }: PaginatedUsersParams = {}
) => {
  try {
    const { data } = await apiInstance.get('/user-profile', {
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
  getUserProfile,
  getUserStats,
  getPaginatedUsers,
};
