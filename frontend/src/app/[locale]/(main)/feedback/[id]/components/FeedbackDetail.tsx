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
import ResourcesList from '@/components/common/ResourcesList';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { useLocale, useTranslations } from 'next-intl';
import { getSessionFeedback } from '@/services/SessionService';
import { showErrorToast } from '@/lib/utils/toast';
import { formatDateFlexible } from '@/lib/utils/formatDateAndTime';
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

  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlayingState] = useState(false);
  const setIsPlaying = useCallback((val: boolean | ((prev: boolean) => boolean)) => {
    setIsPlayingState(val);
  }, []);

  const examplePositive = feedbackDetail?.feedback?.examplePositive || [];

  const exampleNegative = feedbackDetail?.feedback?.exampleNegative || [];

  const recommendations = feedbackDetail?.feedback?.recommendations || [];

  const totalScore =
    (feedbackDetail?.feedback?.scores.structure ?? 0) +
    (feedbackDetail?.feedback?.scores.empathy ?? 0) +
    (feedbackDetail?.feedback?.scores.focus ?? 0) +
    (feedbackDetail?.feedback?.scores.clarity ?? 0);

  const maxScore = Object.values(feedbackDetail?.feedback?.scores ?? {}).length * 5;

  if (isLoading) {
    return <FeedbackDetailLoadingPage />;
  }

  return (
    <div className="flex flex-col items-center gap-12">
      <div className="flex flex-col gap-8 w-full">
        <div className="text-2xl font-bold text-bw-90 text-left w-full">{t('title')}</div>

        {feedbackDetail?.title && (
          <div className="bg-marigold-10 p-8 flex flex-col gap-1 rounded-lg text-center w-full">
            <div className="font-semibold text-2xl text-marigold-90">{feedbackDetail.title}</div>
            <div className="text-marigold-90">
              {formatDateFlexible(feedbackDetail?.createdAt, locale, true)}
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col md:flex-row gap-12 max-w-5xl items-center w-full justify-between">
        <DonutChart totalScore={totalScore} maxScore={maxScore} />
        <ProgressBars data={progressBarData} />
      </div>

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
            <div className="mt-6">
              <p className="text-xs text-bw-40">{tCommon('aiGeneratedDisclaimer')}</p>
            </div>
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="suggestion">
          <AccordionTrigger>{t('accordion.suggestion')}</AccordionTrigger>
          <AccordionContent>
            {feedbackDetail?.feedback?.documentNames &&
            feedbackDetail.feedback.documentNames.length > 0 ? (
              <ResourcesList resources={feedbackDetail.feedback.documentNames} columns={2} />
            ) : (
              <EmptyListComponent itemType={tCommon('resources.title')} />
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
