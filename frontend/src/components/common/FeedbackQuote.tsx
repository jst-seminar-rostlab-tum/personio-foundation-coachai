import { FeedbackQuoteProps } from '@/interfaces/FeedbackQuoteProps';
import { CheckCircle, CircleX, InfoIcon } from 'lucide-react';

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
        return <CheckCircle size={18} className="text-green-300" />;
      case 'Cross':
        return <CircleX size={18} className="text-red-300" />;
      case 'Info':
        return <InfoIcon size={18} className="text-marigold-50" />;
      default:
        return null;
    }
  };
  const iconElement = getIcon(icon || 'Info');
  return (
    <div className="w-full flex gap-3 px-2">
      {iconElement}
      <div className="flex flex-col gap-2">
        <div className="text-xl">{heading}</div>
        {feedback && <div className="text-base">{feedback}</div>}
        {(quote || improvedQuote) && (
          <div className="flex flex-col gap-1 bg-bw-10 border-1 border-bw-20 p-2">
            {quote && <div className="text-base italic">{quote}</div>}
            {improvedQuote && (
              <div className="text-base italic text-green-200">{improvedQuote}</div>
            )}
          </div>
        )}
        {recommendation && <div className="text-base">{recommendation}</div>}
      </div>
    </div>
  );
}
