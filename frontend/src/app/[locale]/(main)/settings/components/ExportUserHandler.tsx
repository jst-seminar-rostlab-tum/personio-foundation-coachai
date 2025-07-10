'use client';

import { useState } from 'react';
import { UserProfileService } from '@/services/UserProfileService';
import { useTranslations } from 'next-intl';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
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
} from '@/components/ui/AlertDialog';

interface ExportUserHandlerProps {
  children: React.ReactNode;
}

export function ExportUserHandler({ children }: ExportUserHandlerProps) {
  const [loading, setLoading] = useState(false);
  const tCommon = useTranslations('Common');
  const tSettings = useTranslations('Settings');

  async function handleExportUser() {
    setLoading(true);
    try {
      const blob = await UserProfileService.exportUserData(api);
      const zipBlob = blob instanceof Blob ? blob : new Blob([blob], { type: 'application/zip' });
      const url = window.URL.createObjectURL(zipBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'user_data_export.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showSuccessToast(tSettings('exportSuccess'));
    } catch (error) {
      showErrorToast(error, tSettings('exportError'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{children}</AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{tSettings('exportData')}</AlertDialogTitle>
          <AlertDialogDescription>{tSettings('exportDataConfirmDesc')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{tCommon('cancel')}</AlertDialogCancel>
          <AlertDialogAction onClick={handleExportUser} disabled={loading}>
            {loading ? tSettings('exporting') : tCommon('export')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
