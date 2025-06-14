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
import { createFeedback } from '@/services/FeedbackService';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

export default function FeedbackDialog() {
  const t = useTranslations('Feedback.feedbackDialog');
  const [rating, setRating] = useState(0);
  const [ratingDescription, setRatingDescription] = useState('');
  const rateFeedback = () => {
    try {
      createFeedback({
        rating,
        comment: ratingDescription,
      });
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="self-end">{t('open')}</Button>
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
