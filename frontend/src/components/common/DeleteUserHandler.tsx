import { useState } from 'react';
import { deleteUser } from '@/services/DeleteUser';
import { useTranslations } from 'next-intl';
import { X } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
} from '../ui/AlertDialog';

export function useDeleteUser() {
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMessage, setDialogMessage] = useState<string | null>(null);
  const t = useTranslations('TrainingSettings');

  async function handleDeleteUser(userId: string) {
    setLoading(true);
    try {
      await deleteUser(userId);
      setDialogMessage(t('userDeleted'));
      setDialogOpen(true);
    } catch (error: unknown) {
      let message = t('deleteFailed');
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const axiosError = error as { response?: { status: number } };
        switch (axiosError.response?.status) {
          case 400:
            message = t('invalidUserId');
            break;
          case 401:
            message = t('authFailed');
            break;
          case 403:
            message = t('notAuthorized');
            break;
          case 404:
          case 422:
            message = t('userNotFound');
            break;
          case 500:
            message = t('serverError');
            break;
          default:
            message = t('deleteFailed');
        }
      }
      setDialogMessage(message);
      setDialogOpen(true);
    } finally {
      setLoading(false);
    }
  }

  function RenderDialog() {
    return (
      <AlertDialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <AlertDialogContent>
          <div className="absolute top-3 right-3">
            <AlertDialogCancel asChild>
              <button
                aria-label="Close"
                className="p-0.5 rounded hover:bg-flame-50 transition"
                onClick={() => setDialogOpen(false)}
                type="button"
              >
                <X className="w-5 h-5" />
              </button>
            </AlertDialogCancel>
          </div>
          <AlertDialogHeader>
            <AlertDialogDescription className="text-center">{dialogMessage}</AlertDialogDescription>
          </AlertDialogHeader>
        </AlertDialogContent>
      </AlertDialog>
    );
  }
  return { handleDeleteUser, loading, RenderDialog, setDialogOpen };
}
