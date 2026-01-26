'use client';

import { useState, useEffect, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { UserProfileService as ClientUserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiClient';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { useTranslations } from 'next-intl';
import type { UserProfile } from '@/interfaces/models/UserProfile';
import { AccountRole } from '@/interfaces/models/UserProfile';
import { UserRoles } from '@/lib/constants/userRoles';

/**
 * Props for the user detail dialog.
 */
interface UserDialogProps {
  userId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

/**
 * Shows user details and allows editing per-user session limits.
 */
export default function UserDialog({ userId, isOpen, onClose, onUpdate }: UserDialogProps) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [sessionLimit, setSessionLimit] = useState<number | string>(0);
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');
  const userRoles = UserRoles();

  /**
   * Fetches the selected user's profile for display and editing.
   */
  const fetchUserProfile = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    try {
      const userProfile = await ClientUserProfileService.getUserProfileById(api, userId);
      setUser(userProfile);
      setSessionLimit(userProfile.dailySessionLimit || 0);
    } catch (error) {
      showErrorToast(error, 'Error loading user profile');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId && isOpen) {
      fetchUserProfile();
    }
  }, [userId, isOpen, fetchUserProfile]);

  /**
   * Saves the updated session limit and refreshes the user profile.
   */
  const handleSaveSessionLimit = async () => {
    if (!userId) return;

    const numericValue = parseInt(sessionLimit.toString(), 10) || 0;
    setSaving(true);
    try {
      await ClientUserProfileService.updateDailySessionLimit(api, userId, numericValue);
      showSuccessToast(t('sessionSuccess'));
      await fetchUserProfile();
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      showErrorToast(error, t('sessionFailed'));
    } finally {
      setSaving(false);
    }
  };

  /**
   * Updates the local session limit input value.
   */
  const handleSessionLimitChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setSessionLimit(value);
  };

  if (!user && !loading) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="w-[95vw] max-w-md sm:mx-0">
        <DialogHeader>
          <DialogTitle>{t('userDetails')}</DialogTitle>
        </DialogHeader>

        {user && (
          <div className="space-y-3 sm:space-y-4">
            <div>
              <label className="block text-sm font-medium text-bw-70 mb-1">{t('email')}</label>
              <div className="text-sm text-bw-60 bg-bw-10 px-3 py-2 rounded border break-words">
                {user.email}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-bw-70 mb-1">{t('fullName')}</label>
              <div className="text-sm text-bw-60 bg-bw-10 px-3 py-2 rounded border">
                {user.fullName || '-'}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-bw-70 mb-1">{t('role')}</label>
              <div className="text-sm text-bw-60 bg-bw-10 px-3 py-2 rounded border">
                {user.accountRole === AccountRole.admin ? t('admin') : t('user')}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-bw-70 mb-1">
                {t('professionalRole')}
              </label>
              <div className="text-sm text-bw-60 bg-bw-10 px-3 py-2 rounded border">
                {userRoles.find((role) => role.id === user.professionalRole)?.label ||
                  user.professionalRole ||
                  '-'}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-bw-70 mb-1">
                {t('dailySessionLimit')}
              </label>
              <div className="flex flex-col md:flex-row gap-2">
                <Input
                  type="number"
                  min="0"
                  value={sessionLimit}
                  onChange={handleSessionLimitChange}
                  className="w-full md:flex-1 text-sm text-bw-60 bg-bw-10 px-3 py-2 rounded border border-bw-20 focus:border-bw-20 focus-visible:outline-none focus-visible:ring-0"
                />
                <Button
                  onClick={handleSaveSessionLimit}
                  disabled={saving || loading}
                  className="w-full md:w-auto"
                >
                  {saving ? tCommon('saving') : tCommon('save')}
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-bw-70 mb-1">
                {t('sessionsUsedToday')}
              </label>
              <div className="text-sm text-bw-60 bg-bw-10 px-3 py-2 rounded border">
                {user.sessionsCreatedToday || 0}
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
