'use client';

import {
  ChartNoAxesColumnIncreasingIcon,
  CheckCircle,
  CircleX,
  Clock,
  MessageCircle,
  MessageCircleQuestion,
  Mic,
  PlayIcon,
} from 'lucide-react';
import Progress from '@/components/ui/Progress';
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
import { showErrorToast } from '@/lib/toast';
import { convertTimeToMinutes, formattedDate } from '@/lib/utils';
import { api } from '@/services/ApiClient';
import FeedbackQuote from './FeedbackQuote';
import FeedbackDialog from './FeedbackDialog';
import FeedbackDetailLoadingPage from '../loading';

interface FeedbackDetailProps {
  sessionId: string;
}

export default function FeedbackDetail({ sessionId }: FeedbackDetailProps) {
  const t = useTranslations('Feedback');
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
        showErrorToast(error, t('getSessionDetailError'));
      }
    },
    [setFeedbackDetail, setIsLoading, t]
  );

  useEffect(() => {
    getFeedbackDetail(sessionId);
  }, [getFeedbackDetail, sessionId]);

  const progressBarData = [
    { key: t('progressBars.structure'), value: feedbackDetail?.feedback?.scores.structure ?? 0 },
    { key: t('progressBars.empathy'), value: feedbackDetail?.feedback?.scores.empathy ?? 0 },
    { key: t('progressBars.focus'), value: feedbackDetail?.feedback?.scores.focus ?? 0 },
    { key: t('progressBars.clarity'), value: feedbackDetail?.feedback?.scores.clarity ?? 0 },
  ];

  const roundCardStats = [
    {
      key: t('stats.sessionLength'),
      value: convertTimeToMinutes(feedbackDetail?.feedback?.sessionLengthS ?? 0),
      icon: 'Clock',
    },
    {
      key: t('stats.goalsAchieved'),
      value: `${feedbackDetail?.feedback?.goalsAchieved.length ?? 0} / ${
        feedbackDetail?.goalsTotal.length ?? 0
      }`,
      icon: 'Check',
    },
  ];

  const examplePositive = feedbackDetail?.feedback?.examplePositive || [];

  const exampleNegative = feedbackDetail?.feedback?.exampleNegative || [];

  const recommendations = feedbackDetail?.feedback?.recommendations || [];

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'Mic':
        return <Mic size={20} />;
      case 'Message':
        return <MessageCircle size={20} />;
      case 'Clock':
        return <Clock size={20} />;
      default:
        return <MessageCircleQuestion size={20} />;
    }
  };
  if (isLoading) {
    return <FeedbackDetailLoadingPage />;
  }
  return (
    <div className="flex flex-col items-center gap-8">
      <div className="text-2xl ">{t('title')}</div>
      <div className="h-20 bg-marigold-10 px-4 py-5 rounded-md text-center w-full">
        <div className="text-lg text-marigold-90">{feedbackDetail?.title}</div>
        <div className="text-base text-marigold-95">
          {formattedDate(feedbackDetail?.createdAt, locale)}
        </div>
      </div>
      <FeedbackDialog sessionId={sessionId} />
      <div className="flex gap-3 items-center w-full justify-between">
        <div className="flex flex-col gap-4 p-2.5 flex-1">
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
        <div className="size-25 rounded-full bg-marigold-10 flex items-center justify-center text-2xl text-marigold-90">
          {feedbackDetail?.feedback?.overallScore ?? 0}%
        </div>
      </div>
      <div className="my-4 mx-2 h-px w-full bg-bw-30" />

      <div className="flex justify-evenly w-full">
        {roundCardStats.map((stat) => (
          <div className="flex gap-2 items-center" key={stat.key}>
            <div className="rounded-full size-11 border-1 border-bw-30 bg-bw-10 flex items-center justify-center">
              {getIcon(stat.icon)}
            </div>
            <div className="flex flex-col gap-1 justify-between">
              <span className="text-base">{stat.key}</span>
              <span className="text-md">{stat.value}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="my-4 mx-2 h-px w-full bg-bw-30" />
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
