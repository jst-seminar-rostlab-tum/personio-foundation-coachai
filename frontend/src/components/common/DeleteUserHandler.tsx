'use client';

import { UserProfileService } from '@/services/UserProfileService';
import { useTranslations } from 'next-intl';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { DeleteConfirmButton } from './DeleteConfirmButton';

interface DeleteUserHandlerProps {
  id?: string;
  onDeleteSuccess: () => void;
}

export function DeleteUserHandler({ id, onDeleteSuccess }: DeleteUserHandlerProps) {
  const tCommon = useTranslations('Common');

  async function handleDeleteUser(deleteUserId?: string) {
    try {
      await UserProfileService.deleteUser(api, deleteUserId);
      showSuccessToast(tCommon('deleteAccountSuccess'));
      onDeleteSuccess();
    } catch (error) {
      showErrorToast(error, tCommon('deleteAccountError'));
    }
  }

  return <DeleteConfirmButton onConfirm={() => handleDeleteUser(id)} />;
}
