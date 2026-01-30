'use client';

import { useState } from 'react';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/Button';
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

/**
 * Exports the current user's data as a downloadable archive.
 */
export function ExportUserHandler() {
  const [loading, setLoading] = useState(false);
  const tCommon = useTranslations('Common');
  const tSettings = useTranslations('Settings');

  /**
   * Fetches user data, builds a download, and triggers file save.
   */
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
      <AlertDialogTrigger asChild>
        <Button variant="default" className="w-full">
          <Download className="w-4 h-4" />
          <span className="hidden sm:inline">{tSettings('export')}</span>
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{tSettings('exportData')}</AlertDialogTitle>
          <AlertDialogDescription>{tSettings('exportDataConfirmDesc')}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{tCommon('cancel')}</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleExportUser}
            disabled={loading}
            className="bg-bw-70 text-background hover:bg-bw-50"
          >
            {loading ? tSettings('exporting') : tSettings('export')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
