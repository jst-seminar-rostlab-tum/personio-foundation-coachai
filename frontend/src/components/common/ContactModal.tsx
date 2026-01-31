'use client';

import { useTranslations } from 'next-intl';
import { Dialog, DialogContent } from '../ui/Dialog';

/**
 * Props for the contact modal.
 */
interface ContactModalProps {
  isOpen: boolean;
  onClose: () => void;
  email?: string;
}

/**
 * Displays a modal with contact information and email link.
 */
export function ContactModal({
  isOpen,
  onClose,
  email = 'coach.ai@personio.foundation',
}: ContactModalProps) {
  const tCommon = useTranslations('Common');

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-bw-70">{tCommon('contactModal.title')}</h2>
        </div>
        <div className="space-y-4">
          <p className="text-bw-60">
            {tCommon('contactModal.description')}{' '}
            <a
              href={`mailto:${email}`}
              className="text-forest-70 hover:text-forest-90 font-medium underline transition-colors"
            >
              {email}
            </a>
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
