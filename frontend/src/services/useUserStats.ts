'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { UserStats } from '@/interfaces/UserStats';

export default function useUserStats(userId: string) {
  const [data, setData] = useState<UserStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;

    const fetchUserStats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/user/', {
          headers: {
            'x-user-id': userId,
          },
        });

        setData(response.data);
      } catch (err) {
        console.error('Failed to fetch user stats:', err);
        setError('Failed to load user stats');
      }
    };

    fetchUserStats();
  }, [userId]);

  return { data, error };
}
