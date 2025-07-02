'use client';

import { useState } from 'react';
import { UserProfileService } from '@/services/UserProfileService';
import { useTranslations } from 'next-intl';
import { showErrorToast, showSuccessToast } from '@/lib/component-utils/toast';
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
}

export function DeleteUserHandler({ children, id }: DeleteUserHandlerProps) {
  const [loading, setLoading] = useState(false);
  const tCommon = useTranslations('Common');

  async function handleDeleteUser(deleteUserId?: string) {
    setLoading(true);
    try {
      await UserProfileService.deleteUser(api, deleteUserId);
      showSuccessToast(tCommon('deleteAccountSuccess'));
      if (!deleteUserId) {
        redirect('/');
      }
    } catch (error) {
      showErrorToast(error, tCommon('deleteAccountError'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{children}</AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{tCommon('areYouSure')}</AlertDialogTitle>
          <AlertDialogDescription>{tCommon('deleteAccountConfirmDesc')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{tCommon('cancel')}</AlertDialogCancel>
          <AlertDialogAction onClick={() => handleDeleteUser(id)} disabled={loading}>
            {loading ? tCommon('deleting') : tCommon('confirm')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
