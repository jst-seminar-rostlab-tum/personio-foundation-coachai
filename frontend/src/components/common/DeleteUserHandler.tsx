import { useState } from 'react';
import { UserProfileService } from '@/services/client/UserProfileService';
import { useTranslations } from 'next-intl';
import { DeleteUserHandlerProps } from '@/interfaces/DeleteUserHandlerProps';
import { showErrorToast, showSuccessToast } from '@/lib/toast';
import { redirect } from 'next/navigation';
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

export function DeleteUserHandler({ children, id }: DeleteUserHandlerProps) {
  const [loading, setLoading] = useState(false);
  const t = useTranslations('Common');

  async function handleDeleteUser(deleteUserId?: string) {
    setLoading(true);
    try {
      await UserProfileService.deleteUser(deleteUserId);
      showSuccessToast(t('deleteAccountSuccess'));
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
