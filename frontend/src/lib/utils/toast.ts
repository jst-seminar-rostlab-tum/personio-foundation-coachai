import { toast } from 'sonner';

/**
 * Logs an error and shows an error toast.
 */
export function showErrorToast(error: unknown, message: string) {
  console.error(error);
  toast.error(message);
}

/**
 * Shows a success toast.
 */
export function showSuccessToast(message: string) {
  toast.success(message);
}
