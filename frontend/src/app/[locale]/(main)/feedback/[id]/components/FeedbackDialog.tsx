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
import { showErrorToast, showSuccessToast } from '@/lib/toast';
import { reviewService } from '@/services/client/ReviewService';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

export default function FeedbackDialog({ sessionId }: { sessionId: string }) {
  const t = useTranslations('Feedback.feedbackDialog');
  const [rating, setRating] = useState(0);
  const [ratingDescription, setRatingDescription] = useState('');

  const resetForm = () => {
    setRating(0);
    setRatingDescription('');
  };

  const handleOpenChange = (open: boolean) => {
    if (open) {
      resetForm();
    }
  };

  const rateFeedback = async () => {
    try {
      await reviewService.createReview({
        rating,
        comment: ratingDescription,
        sessionId,
      });
      showSuccessToast(t('submitFeedbackSuccess'));
    } catch (error) {
      showErrorToast(error, t('submitFeedbackError'));
    }
  };

  return (
    <Dialog onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button size="full">{t('open')}</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-2xl">{t('title')}</DialogTitle>
          <DialogDescription className="text-marigold-90">{t('description')}</DialogDescription>
        </DialogHeader>

        <Rating
          className="mx-auto"
          defaultValue={0}
          value={rating}
          onValueChange={(value) => setRating(value)}
        >
          {Array.from({ length: 5 }).map((_, index) => (
            <RatingButton className="text-marigold-50" size={30} key={index} />
          ))}
        </Rating>
        <Textarea
          value={ratingDescription}
          onChange={(e) => setRatingDescription(e.target.value)}
        />

        <DialogClose asChild>
          <Button
            variant={rating ? 'default' : 'disabled'}
            onClick={rateFeedback}
            disabled={!rating}
          >
            {t('rate')}
          </Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );
}
