import { useEffect, useState, useRef } from 'react';
import { ChevronUp } from 'lucide-react';
import { useTranslations } from 'next-intl';
import type { SessionLiveFeedback } from '@/interfaces/models/Session';

/**
 * Props for the live feedback list.
 */
interface SessionLiveFeedbackProps {
  liveFeedbacks: SessionLiveFeedback[];
}

/**
 * Shows AI live feedback suggestions with highlight for new items.
 */
export default function SessionLiveFeedback({ liveFeedbacks }: SessionLiveFeedbackProps) {
  const t = useTranslations('Session.LiveFeedback');
  const tCommon = useTranslations('Common');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const [newLiveFeedbackIds, setNewLiveFeedbackIds] = useState<string[]>([]);
  const timeoutsRef = useRef<{ [id: string]: NodeJS.Timeout }>({});

  const prevLiveFeedbackIdsRef = useRef<string[]>([]);

  const liveFeedbackContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const currentIds = liveFeedbacks.map((fb) => fb.id);
    const prevIds = prevLiveFeedbackIdsRef.current;

    const newIds = currentIds.filter((id) => !prevIds.includes(id));

    newIds.forEach((id) => {
      setNewLiveFeedbackIds((prev) => [...prev, id]);
      timeoutsRef.current[id] = setTimeout(() => {
        setNewLiveFeedbackIds((prev) => prev.filter((recentId) => recentId !== id));
        delete timeoutsRef.current[id];
      }, 5000);
    });

    newLiveFeedbackIds.forEach((id) => {
      if (!currentIds.includes(id)) {
        clearTimeout(timeoutsRef.current[id]);
        setNewLiveFeedbackIds((prev) => prev.filter((recentId) => recentId !== id));
        delete timeoutsRef.current[id];
      }
    });

    if (newIds.length > 0 && liveFeedbackContainerRef.current) {
      liveFeedbackContainerRef.current.scrollTop = 0;
    }

    prevLiveFeedbackIdsRef.current = currentIds;
  }, [liveFeedbacks, newLiveFeedbackIds]);

  useEffect(() => {
    const timeouts = { ...timeoutsRef.current };
    return () => {
      Object.values(timeouts).forEach(clearTimeout);
    };
  }, []);

  return (
    <>
      <div
        className="flex items-center justify-start gap-2 py-4 border-y border-bw-50 hover:cursor-pointer group relative z-20"
        onClick={() => setShowSuggestions((prev) => !prev)}
      >
        <div className="w-full max-w-7xl mx-auto flex items-center gap-2 px-[clamp(1.25rem,4vw,4rem)]">
          <ChevronUp
            className={`w-5 h-5 transition-transform duration-600 ${showSuggestions ? 'rotate-180' : ''}`}
          />
          <span className="font-medium text-font-dark text-sm group-hover:underline">
            {t('title')}
          </span>
        </div>
      </div>
      <div
        className={`w-full overflow-hidden transition-all duration-600 ease-in-out ${
          showSuggestions ? 'max-h-[30vh] md:max-h-[25vh]' : 'max-h-0'
        }`}
      >
        <div className="w-full">
          <div
            ref={liveFeedbackContainerRef}
            className="w-full max-w-7xl mx-auto flex flex-col overflow-y-auto 
            [&::-webkit-scrollbar]:hidden 
            [-ms-overflow-style:'none'] 
            [scrollbar-width:'none'] 
            p-6 
            px-[clamp(1.25rem,4vw,4rem)] 
            max-h-[30vh] md:max-h-[25vh]"
          >
            <ul className="flex flex-col gap-4 w-full">
              {liveFeedbacks.map((liveFeedback) => (
                <li
                  key={liveFeedback.id}
                  className={`rounded-lg border p-4 transition-colors duration-300 ${
                    newLiveFeedbackIds.includes(liveFeedback.id)
                      ? 'border-forest-90 bg-black text-white'
                      : 'border-bw-40 bg-custom-beige'
                  }`}
                >
                  <div className="font-semibold mb-1">{liveFeedback.heading}</div>
                  <div className="text-sm leading-snug">{liveFeedback.feedbackText}</div>
                </li>
              ))}
            </ul>
            <div className="mt-4 text-center">
              <p className="text-xs text-bw-50">{tCommon('aiGeneratedDisclaimer2')}</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
