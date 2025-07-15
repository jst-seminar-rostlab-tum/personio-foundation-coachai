import { useState } from 'react';
import { Trash2, Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
} from '@/components/ui/AlertDialog';
import { Button } from '../ui/Button';

interface DeleteConfirmButtonProps {
  onConfirm: () => Promise<void>;
  isButton?: boolean;
}

export function DeleteConfirmButton({ onConfirm, isButton = false }: DeleteConfirmButtonProps) {
  const t = useTranslations('Common');
  const [open, setOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        {isButton ? (
          <Button variant="destructive">{t('deleteAccount')}</Button>
        ) : (
          <button
            type="button"
            className="text-bw-40 hover:text-flame-50 transition-colors cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              setOpen(true);
            }}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Trash2 className="w-5 h-5" />
            )}
          </button>
        )}
      </AlertDialogTrigger>
      <AlertDialogContent onClick={(e) => e.stopPropagation()}>
        <AlertDialogHeader className="gap-4">
          <AlertDialogTitle className="text-xl">{t('areYouSure')}</AlertDialogTitle>
          <AlertDialogDescription className="text-base leading-relaxed">
            {t('deleteAccountConfirmDesc')}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{t('cancel')}</AlertDialogCancel>
          <AlertDialogAction
            onClick={async () => {
              setIsDeleting(true);
              await onConfirm();
              setIsDeleting(false);
              setOpen(false);
            }}
          >
            {t('confirm')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
