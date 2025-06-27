'use client';

import {
  ChartNoAxesColumnIncreasingIcon,
  CheckCircle,
  CircleX,
  Clock,
  PlayIcon,
} from 'lucide-react';
import Progress from '@/components/ui/Progress';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { FeedbackResponse } from '@/interfaces/FeedbackQuoteProps';
import { useCallback, useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { getSessionFeedback } from '@/services/client/SessionService';
import { showErrorToast } from '@/lib/toast';
import FeedbackQuote from './FeedbackQuote';
import FeedbackDialog from './FeedbackDialog';
import FeedbackDetailLoadingPage from '../loading';

export default function FeedbackDetail({ sessionId }: { sessionId: string }) {
  const t = useTranslations('Feedback');
  const [feedbackDetail, setFeedbackDetail] = useState<FeedbackResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const getFeedbackDetail = useCallback(
    async (id: string) => {
      try {
        const response = await getSessionFeedback(id);
        if (response.status === 202) {
          setTimeout(() => {
            getFeedbackDetail(id);
          }, 2000);
          return;
        }

        if (response.status === 200) {
          setFeedbackDetail(response.data);
          setIsLoading(false);
          return;
        }

        throw new Error('Failed to get session feedback');
      } catch (error) {
        setIsLoading(false);
        showErrorToast(error, t('getSessionDetailError'));
      }
    },
    [setFeedbackDetail, setIsLoading, t]
  );

  useEffect(() => {
    getFeedbackDetail(sessionId);
  }, [getFeedbackDetail, sessionId]);

  const convertTimeToMinutes = (seconds: number) => {
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();

    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}.${month}.${year}, ${hours}:${minutes}`;
  };

  const progressBarData = [
    { key: t('progressBars.structure'), value: feedbackDetail?.feedback?.scores.structure ?? 0 },
    { key: t('progressBars.empathy'), value: feedbackDetail?.feedback?.scores.empathy ?? 0 },
    { key: t('progressBars.focus'), value: feedbackDetail?.feedback?.scores.focus ?? 0 },
    { key: t('progressBars.clarity'), value: feedbackDetail?.feedback?.scores.clarity ?? 0 },
  ];

  const examplePositive = feedbackDetail?.feedback?.examplePositive || [];

  const exampleNegative = feedbackDetail?.feedback?.exampleNegative || [];

  const recommendations = feedbackDetail?.feedback?.recommendations || [];

  // Calculate values for the donut chart
  const radius = 70;
  const stroke = 8;
  const normalizedRadius = radius;
  const circumference = 2 * Math.PI * normalizedRadius;
  const percent = feedbackDetail?.feedback?.overallScore ?? 0;

  // Animation state for the donut fill
  const [animatedPercent, setAnimatedPercent] = useState(0);
  useEffect(() => {
    function animate(now: number) {
      const elapsed = now - startRef.current;
      const progress = Math.min(elapsed / durationRef.current, 1);
      setAnimatedPercent(Math.round(percentRef.current * progress));
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }
    const durationRef = { current: 500 };
    const startRef = { current: 0 };
    const percentRef = { current: percent };
    if (percent > 0) {
      setAnimatedPercent(0);
      durationRef.current = 500;
      startRef.current = performance.now();
      percentRef.current = percent;
      requestAnimationFrame(animate);
    } else {
      setAnimatedPercent(0);
    }
  }, [percent]);
  const offset = circumference * (1 - animatedPercent / 100);

  if (isLoading) {
    return <FeedbackDetailLoadingPage />;
  }
  return (
    <div className="flex flex-col items-center gap-16">
      <div className="text-2xl ">{t('title')}</div>
      <div className="h-20 bg-marigold-10 px-4 py-5 rounded-md text-center w-full">
        <div className="text-lg text-marigold-90">{feedbackDetail?.title}</div>
        <div className="text-base text-marigold-95">
          {formatDateTime(feedbackDetail?.createdAt ?? '')}
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-12 items-center w-full justify-between">
        {/* Donut Chart */}
        <div className="flex items-center w-64 h-64 aspect-square max-w-xs flex-shrink-0 mx-auto md:mx-0">
          <div className="relative w-full h-full flex items-center justify-center">
            <svg
              className="w-full h-full"
              viewBox="0 0 160 160"
              aria-label="Overall Score Donut Chart"
            >
              <circle
                cx="80"
                cy="80"
                r={radius}
                fill="none"
                strokeWidth={stroke}
                className="stroke-bw-20"
              />
              <circle
                cx="80"
                cy="80"
                r={radius}
                fill="none"
                strokeWidth={stroke}
                className="stroke-marigold-50"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                strokeLinecap="round"
                transform="rotate(-90 80 80)"
              />
            </svg>
            <div
              className="absolute top-1/2 left-1/2 flex flex-col items-center justify-center w-full gap-2"
              style={{ transform: 'translate(-50%, -50%)' }}
            >
              <span className="font-medium text-5xl fill-bw-60 text-bw-60">{percent}%</span>{' '}
              <span className="text-base text-bw-40 mt-1 flex items-baseline gap-1.5">
                <span className="text-xl font-semibold">
                  {feedbackDetail?.feedback?.goalsAchieved.length ?? 0}/
                  {feedbackDetail?.goalsTotal.length ?? 0}
                </span>
                {t('stats.goalsAchieved')}
              </span>
            </div>
          </div>
        </div>
        {/* Progress Bars */}
        <div className="flex flex-col gap-6 flex-1 w-full p-2">
          {progressBarData.map((item) => (
            <div key={item.key} className="flex flex-col gap-2">
              <div className="flex justify-between text-base">
                <span>{item.key}</span>
                <span>{item.value}%</span>
              </div>
              <Progress className="w-full" value={item.value} />
            </div>
          ))}
        </div>
      </div>

      <FeedbackDialog sessionId={sessionId} />
      {/* Replay Conversation */}
      <div className="flex items-center justify-center gap-3 mx-1 px-3 w-full h-20 bg-bw-10 rounded-md">
        <div className="size-11 rounded-full bg-marigold-50 flex items-center justify-center">
          <PlayIcon size={20} className="text-white" />
        </div>
        <div className="flex flex-col justify-between flex-1">
          <span className="text-md">{t('listenConversation')}</span>
          <div className="flex gap-3 items-center">
            <Progress className="w-10 flex-1" value={62} />
            <div className="flex gap-1 items-center text-base text-bw-40">
              <Clock size={13} />
              <span>{convertTimeToMinutes(feedbackDetail?.feedback?.sessionLengthS ?? 0)}</span>
            </div>
          </div>
        </div>
      </div>
      <Accordion type="multiple">
        <AccordionItem value="feedback">
          <AccordionTrigger>{t('accordian.feedback')}</AccordionTrigger>
          <AccordionContent>
            <div className="flex items-center gap-2 mt-3">
              <CheckCircle size={24} className="text-forest-50" />
              <span className="text-xl">{t('detailedFeedback.positive')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {examplePositive.map((example, index) => (
                <FeedbackQuote key={index} {...example} icon="Check" />
              ))}
            </div>

            <div className="flex items-center gap-2 mt-10">
              <CircleX size={24} className="text-flame-50" />
              <span className="text-xl">{t('detailedFeedback.negative')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {exampleNegative.map((negative, index) => (
                <FeedbackQuote key={index} {...negative} icon="Cross" />
              ))}
            </div>

            <div className="flex items-center gap-2 mt-10">
              <ChartNoAxesColumnIncreasingIcon size={24} className="text-marigold-50" />
              <span className="text-xl">{t('detailedFeedback.recommendations')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {recommendations.map((recommendation, index) => (
                <FeedbackQuote key={index} {...recommendation} icon="Info" />
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="suggestion">
          <AccordionTrigger>{t('accordian.suggestion')}</AccordionTrigger>
        </AccordionItem>
        <AccordionItem value="session">
          <AccordionTrigger>{t('accordian.sessions')}</AccordionTrigger>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
