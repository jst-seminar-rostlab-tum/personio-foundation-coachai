'use client';

import { ChartNoAxesColumnIncreasingIcon, CheckCircle, CircleX } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { FeedbackResponse } from '@/interfaces/models/SessionFeedback';
import { useCallback, useEffect, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { getSessionFeedback } from '@/services/SessionService';
import { showErrorToast } from '@/lib/utils/toast';
import { formattedDate } from '@/lib/utils/formatDateAndTime';
import { api } from '@/services/ApiClient';
import AudioPlayer from './AudioPlayer';
import FeedbackQuote from './FeedbackQuote';
import FeedbackDialog from './FeedbackDialog';
import FeedbackDetailLoadingPage from '../loading';
import DonutChart from './DonutChart';
import ProgressBars from './ProgressBars';

interface FeedbackDetailProps {
  sessionId: string;
}

export default function FeedbackDetail({ sessionId }: FeedbackDetailProps) {
  const t = useTranslations('Feedback');
  const tCommon = useTranslations('Common');
  const locale = useLocale();
  const [feedbackDetail, setFeedbackDetail] = useState<FeedbackResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const getFeedbackDetail = useCallback(
    async (id: string) => {
      try {
        const response = await getSessionFeedback(api, id);
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
        showErrorToast(error, t('fetchError'));
      }
    },
    [setFeedbackDetail, setIsLoading, t]
  );

  useEffect(() => {
    getFeedbackDetail(sessionId);
  }, [getFeedbackDetail, sessionId]);

  const progressBarData = [
    { key: tCommon('structure'), value: feedbackDetail?.feedback?.scores.structure ?? 0 },
    { key: tCommon('empathy'), value: feedbackDetail?.feedback?.scores.empathy ?? 0 },
    { key: tCommon('focus'), value: feedbackDetail?.feedback?.scores.focus ?? 0 },
    { key: tCommon('clarity'), value: feedbackDetail?.feedback?.scores.clarity ?? 0 },
  ];

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return h > 0
      ? `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
      : `${m}:${s.toString().padStart(2, '0')}`;
  };

  // Audio player state
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlayingState] = useState(false);
  const setIsPlaying = useCallback((val: boolean | ((prev: boolean) => boolean)) => {
    setIsPlayingState(val);
  }, []);

  const examplePositive = feedbackDetail?.feedback?.examplePositive || [];

  const exampleNegative = feedbackDetail?.feedback?.exampleNegative || [];

  const recommendations = feedbackDetail?.feedback?.recommendations || [];

  if (isLoading) {
    return <FeedbackDetailLoadingPage />;
  }

  return (
    <div className="flex flex-col items-center gap-12">
      <div className="text-2xl font-bold text-bw-90 text-left mb-4 w-full">{t('title')}</div>
      <div className="h-20 bg-marigold-10 px-4 py-5 rounded-md text-center w-full">
        <div className="text-lg text-marigold-90">{feedbackDetail?.title}</div>
        <div className="text-base text-marigold-95">
          {formattedDate(feedbackDetail?.createdAt, locale)}
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-12 px-4 items-center w-full justify-between">
        <DonutChart
          percent={feedbackDetail?.feedback?.overallScore ?? 0}
          goalsAchieved={feedbackDetail?.feedback?.goalsAchieved.length ?? 0}
          goalsTotal={feedbackDetail?.goalsTotal.length ?? 0}
          label={t('stats.goalsAchieved')}
        />
        <ProgressBars data={progressBarData} />
      </div>

      {/* Replay Conversation */}
      <AudioPlayer
        currentTime={currentTime}
        setCurrentTime={setCurrentTime}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        formatTime={formatTime}
        t={t}
      />

      {!feedbackDetail?.hasReviewed && (
        <FeedbackDialog setFeedbackDetail={setFeedbackDetail} sessionId={sessionId} />
      )}

      <Accordion type="multiple">
        <AccordionItem value="feedback">
          <AccordionTrigger>{t('accordion.feedback')}</AccordionTrigger>
          <AccordionContent>
            <div className="flex items-center gap-2 mt-3">
              <CheckCircle size={24} className="text-forest-50" />
              <span className="text-xl">{tCommon('positive')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {examplePositive.map((example, index) => (
                <FeedbackQuote key={index} {...example} icon="Check" />
              ))}
            </div>

            <div className="flex items-center gap-2 mt-10">
              <CircleX size={24} className="text-flame-50" />
              <span className="text-xl">{tCommon('negative')}</span>
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
          <AccordionTrigger>{t('accordion.suggestion')}</AccordionTrigger>
        </AccordionItem>
        <AccordionItem value="session">
          <AccordionTrigger>{t('accordion.sessions')}</AccordionTrigger>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
