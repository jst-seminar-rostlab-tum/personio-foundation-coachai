'use client';

import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/Dialog';
import { Rating, RatingButton } from '@/components/ui/Rating';
import { Textarea } from '@/components/ui/Textarea';
import Checkbox from '@/components/ui/Checkbox';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { reviewService } from '@/services/ReviewService';
import { useTranslations } from 'next-intl';
import { useState, Dispatch, SetStateAction } from 'react';
import { api } from '@/services/ApiClient';
import { FeedbackResponse } from '@/interfaces/models/SessionFeedback';

interface FeedbackDialogProps {
  sessionId: string;
  setFeedbackDetail: Dispatch<SetStateAction<FeedbackResponse | null>>;
}

export default function FeedbackDialog({ sessionId, setFeedbackDetail }: FeedbackDialogProps) {
  const t = useTranslations('Feedback');
  const tCommon = useTranslations('Common');
  const [rating, setRating] = useState(0);
  const [ratingDescription, setRatingDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [shareWithAdmin, setShareWithAdmin] = useState(false);

  const resetForm = () => {
    setRating(0);
    setRatingDescription('');
    setShareWithAdmin(false);
  };

  const handleOpenChange = (open: boolean) => {
    if (open) {
      resetForm();
    }
  };

  const rateFeedback = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      await reviewService.createReview(api, {
        rating,
        comment: ratingDescription,
        sessionId,
        allowAdminAccess: shareWithAdmin,
      });
      showSuccessToast(t('submitSuccess'));
      setFeedbackDetail((prev) => ({ ...prev!, hasReviewed: true }));
    } catch (error) {
      showErrorToast(error, t('submitError'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button size="full">{t('reviewDialog.submitReview')}</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-2xl">{tCommon('reviews')}</DialogTitle>
          <DialogDescription className="text-forest-90">
            {t('reviewDialog.description')}
          </DialogDescription>
        </DialogHeader>

        <Rating
          className="mx-auto"
          defaultValue={0}
          value={rating}
          onValueChange={(value) => setRating(value)}
        >
          {Array.from({ length: 5 }).map((_, index) => (
            <RatingButton className="text-forest-90" size={30} key={index} />
          ))}
        </Rating>
        <Textarea
          value={ratingDescription}
          onChange={(e) => setRatingDescription(e.target.value)}
        />

        <div
          className="flex items-center space-x-2 mt-4 cursor-pointer"
          onClick={() => !isSubmitting && setShareWithAdmin(!shareWithAdmin)}
        >
          <Checkbox checked={shareWithAdmin} disabled={isSubmitting} />
          <label className="text-sm text-bw-70">{t('reviewDialog.shareWithAdmin')}</label>
        </div>

        <DialogClose asChild>
          <Button
            variant={!rating || isSubmitting ? 'disabled' : 'default'}
            onClick={rateFeedback}
            disabled={!rating || isSubmitting}
          >
            {isSubmitting ? tCommon('submitting') : t('reviewDialog.submitReview')}
          </Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );
}
