'use client';

import { UserProfileService } from '@/services/UserProfileService';
import { useTranslations } from 'next-intl';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { DeleteConfirmButton } from './DeleteConfirmButton';

/**
 * Props for deleting a user account.
 */
interface DeleteUserHandlerProps {
  id?: string;
  onDeleteSuccess: () => void;
}

/**
 * Handles user deletion with confirmation and notifications.
 */
export function DeleteUserHandler({ id, onDeleteSuccess }: DeleteUserHandlerProps) {
  const tCommon = useTranslations('Common');

  /**
   * Deletes the user and notifies on success or failure.
   */
  async function handleDeleteUser(deleteUserId?: string) {
    try {
      await UserProfileService.deleteUser(api, deleteUserId);
      showSuccessToast(tCommon('deleteAccountSuccess'));
      onDeleteSuccess();
    } catch (error) {
      showErrorToast(error, tCommon('deleteAccountError'));
    }
  }

  return <DeleteConfirmButton isButton={!id} onConfirm={() => handleDeleteUser(id)} />;
}
