'use client';

import { ChartNoAxesColumnIncreasingIcon, CheckCircle, CircleX } from 'lucide-react';
import { useTranslations } from 'next-intl';

export interface PositiveExample {
  heading: string;
  text: string;
  quote: string;
  guideline: string;
}

export interface NegativeExample {
  heading: string;
  text: string;
  quote: string;
  improved_quote: string;
}

export interface Recommendation {
  heading: string;
  text: string;
}

interface FeedbackQuoteProps {
  type: 'positive' | 'negative' | 'recommendation';
  example?: PositiveExample | NegativeExample;
  recommendation?: Recommendation;
  score?: number;
  icon?: 'Check' | 'Cross' | 'Info';
}

export default function FeedbackQuote({
  type,
  example,
  recommendation,
  score,
  icon = 'Info',
}: FeedbackQuoteProps) {
  const t = useTranslations('Feedback');

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

  const getHeading = () => {
    if (example?.heading) return example.heading;
    if (recommendation?.heading) return recommendation.heading;

    switch (type) {
      case 'positive':
        return t('detailedFeedback.positiveExample');
      case 'negative':
        return t('detailedFeedback.negativeExample');
      case 'recommendation':
        return t('detailedFeedback.recommendation');
      default:
        return '';
    }
  };

  const iconElement = getIcon(icon);

  return (
    <div className="w-full">
      <div className="flex gap-2 items-center">
        {iconElement}
        <div className="text-md">{getHeading()}</div>
        {score && <div className="text-sm text-bw-60">({score}分)</div>}
      </div>
      <div className="flex flex-col gap-2 mt-2 px-7">
        {example && (
          <div className="flex flex-col gap-1 bg-bw-10 border-1 border-bw-20 p-2 text-base rounded-sm">
            <div className="text-base">{example.text}</div>
            <div className="italic">&quot;{example.quote}&quot;</div>
            {'improved_quote' in example && example.improved_quote && (
              <>
                <div>{t('detailedFeedback.nextTime')}</div>
                <div className="italic text-forest-60">&quot;{example.improved_quote}&quot;</div>
              </>
            )}
            {'guideline' in example && example.guideline && (
              <div className="text-sm text-bw-60 mt-1">{example.guideline}</div>
            )}
          </div>
        )}
        {recommendation && (
          <div className="flex flex-col gap-1 bg-bw-10 border-1 border-bw-20 p-2 text-base rounded-sm">
            <div>{recommendation.text}</div>
          </div>
        )}
      </div>
    </div>
  );
}
