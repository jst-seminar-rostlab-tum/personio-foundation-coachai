'use client';

import { FeedbackQuoteProps } from '@/interfaces/Feedback';
import { ChartNoAxesColumnIncreasingIcon, CheckCircle, CircleX } from 'lucide-react';
import { useTranslations } from 'next-intl';

export default function FeedbackQuote({
  heading,
  feedback,
  quote,
  improvedQuote,
  recommendation,
  icon,
}: FeedbackQuoteProps) {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'Check':
        return <CheckCircle size={20} className="text-forest-50" />;
      case 'Cross':
        return <CircleX size={20} className="text-flame-50" />;
      case 'Info':
        return <ChartNoAxesColumnIncreasingIcon size={20} className="text-marigold-50" />;
      default:
        return null;
    }
  };
  const iconElement = getIcon(icon || 'Info');
  const t = useTranslations('Feedback');
  return (
    <div className="w-full">
      <div className="flex gap-2 items-center">
        {iconElement}
        <div className="text-md">{heading}</div>
      </div>
      <div className="flex flex-col gap-2 mt-2 px-7">
        {feedback && <div className="text-base">{feedback}</div>}
        {(quote || improvedQuote) && (
          <div className="flex flex-col gap-1 bg-bw-10 border-1 border-bw-20 p-2 text-base rounded-sm">
            {quote && <div className="italic">&quot;{quote}&quot;</div>}
            {improvedQuote && (
              <>
                <div>{t('detailedFeedback.nextTime')}</div>
                <div className="italic text-forest-60">&quot;{improvedQuote}&quot;</div>
              </>
            )}
          </div>
        )}
        {recommendation && <div className="text-base">{recommendation}</div>}
      </div>
    </div>
  );
}
