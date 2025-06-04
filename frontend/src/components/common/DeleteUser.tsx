/* eslint-disable no-alert */
import { useState } from 'react';
import { deleteUser } from '@/lib/deleteUser';
import { useTranslations } from 'next-intl';

export function useDeleteUser() {
  const [loading, setLoading] = useState(false);
  const t = useTranslations('TrainingSettings');

  async function handleDeleteUser(userId: string) {
    setLoading(true);
    try {
      await deleteUser(userId);
      alert(t('userDeleted'));
    } catch (error: unknown) {
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const axiosError = error as { response?: { status: number } };
        switch (axiosError.response?.status) {
          case 400:
            alert(t('invalidUserId'));
            break;
          case 401:
            alert(t('authFailed'));
            break;
          case 403:
            alert(t('notAuthorized'));
            break;
          case 404:
          case 422:
            alert(t('userNotFound'));
            break;
          case 500:
            alert(t('serverError'));
            break;
          default:
            alert(t('deleteFailed'));
        }
      } else {
        alert(t('deleteFailed'));
      }
    } finally {
      setLoading(false);
    }
  }

  return { handleDeleteUser, loading };
}
