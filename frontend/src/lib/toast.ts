import { toast } from 'sonner';

export function showErrorToast(error: unknown, message: string) {
  console.error(error);
  toast.error(message);
}

export function showSuccessToast(message: string) {
  toast.success(message);
}
