'use client';

import { useState } from 'react';
import { UserProfileService } from '@/services/UserProfileService';
import { useTranslations } from 'next-intl';
import { showErrorToast, showSuccessToast } from '@/lib/toast';
import { redirect } from 'next/navigation';
import { api } from '@/services/ApiClient';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/AlertDialog';

interface DeleteUserHandlerProps {
  id?: string;
  children: React.ReactNode;
  onSuccess?: () => void;
}

export function DeleteUserHandler({ children, id, onSuccess }: DeleteUserHandlerProps) {
  const [loading, setLoading] = useState(false);
  const t = useTranslations('Common');

  async function handleDeleteUser(deleteUserId?: string) {
    setLoading(true);
    try {
      await UserProfileService.deleteUser(api, deleteUserId);
      showSuccessToast(t('deleteAccountSuccess'));
      if (onSuccess) onSuccess();
      if (!deleteUserId) {
        redirect('/');
      }
    } catch (error) {
      showErrorToast(error, t('deleteAccountError'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{children}</AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('deleteAccountConfirmTitle')}</AlertDialogTitle>
          <AlertDialogDescription>{t('deleteAccountConfirmDesc')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{t('cancel')}</AlertDialogCancel>
          <AlertDialogAction onClick={() => handleDeleteUser(id)} disabled={loading}>
            {loading ? t('deleting') : t('confirm')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
