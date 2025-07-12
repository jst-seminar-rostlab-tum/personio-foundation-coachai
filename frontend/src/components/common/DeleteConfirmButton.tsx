import { ReactNode, useState } from 'react';
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

interface DeleteConfirmButtonProps {
  onConfirm: () => void;
  namespace: string;
  ariaLabel?: string;
  className?: string;
  children: ReactNode;
}

export function DeleteConfirmButton({
  onConfirm,
  namespace,
  ariaLabel,
  className,
  children,
}: DeleteConfirmButtonProps) {
  const t = useTranslations(namespace);
  const [open, setOpen] = useState(false);

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <button
          type="button"
          className={className}
          aria-label={ariaLabel || t('deleteConfirmDelete')}
          onClick={(e) => {
            e.stopPropagation();
            setOpen(true);
          }}
        >
          {children}
        </button>
      </AlertDialogTrigger>
      <AlertDialogContent onClick={(e) => e.stopPropagation()}>
        <AlertDialogHeader className="gap-4">
          <AlertDialogTitle className="text-xl">{t('deleteConfirmTitle')}</AlertDialogTitle>
          <AlertDialogDescription className="text-base leading-relaxed">
            {t('deleteConfirmDescription')}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{t('deleteConfirmCancel')}</AlertDialogCancel>
          <AlertDialogAction
            onClick={() => {
              onConfirm();
              setOpen(false);
            }}
          >
            {t('deleteConfirmDelete')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
