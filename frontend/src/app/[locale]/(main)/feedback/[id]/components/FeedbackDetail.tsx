'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
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
import { Button } from '@/components/ui/Button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { api } from '@/services/Api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import FeedbackQuote from './FeedbackQuote';

const Loading = dynamic(() => import('../loading'), { ssr: false });

type FeedbackType = {
  id: string;
  session_id: string;
  scores: {
    structure: number;
    empathy: number;
    focus: number;
    clarity: number;
    [key: string]: number;
  };
  tone_analysis: {
    positive: number;
    neutral: number;
    negative: number;
    [key: string]: number;
  };
  overall_score: number;
  transcript_uri: string;
  speak_time_percent: number;
  questions_asked: number;
  session_length_s: number;
  goals_achieved: number;
  example_positive: Array<{
    heading: string;
    feedback: string;
    quote: string;
  }>;
  example_negative: Array<{
    heading: string;
    feedback: string;
    quote: string;
    improved_quote?: string;
  }>;
  recommendations: Array<{
    heading: string;
    recommendation: string;
  }>;
  status: string;
  created_at: string;
  updated_at: string;
};

export default function FeedbackDetail() {
  const t = useTranslations('Feedback');
  const params = useParams();
  const [feedback, setFeedback] = useState<FeedbackType | null>(null);
  const [isPending, setIsPending] = useState(false);

  useEffect(() => {
    const id = params?.id;
    if (!id) return;
    api
      .get(`/session-feedback/${id}`)
      .then((res) => {
        console.warn('res.data', res.data);
        if (res.status === 202) {
          setIsPending(true);
          setFeedback(null);
        } else {
          setIsPending(false);
          setFeedback(res.data);
        }
      })
      .catch(() => {
        setIsPending(false);
        setFeedback(null);
      });
  }, [params]);

  if (isPending) return <Loading />;

  if (!feedback) return <div>Loading...</div>;

  const progressBarData = [
    { key: t('progressBars.structure'), value: feedback.scores?.structure ?? 0 },
    { key: t('progressBars.empathy'), value: feedback.scores?.empathy ?? 0 },
    { key: t('progressBars.focus'), value: feedback.scores?.focus ?? 0 },
    { key: t('progressBars.clarity'), value: feedback.scores?.clarity ?? 0 },
  ];

  const roundCardStats = [
    { key: t('stats.speakingTime'), value: `${feedback.speak_time_percent ?? 0}%`, icon: 'Mic' },
    { key: t('stats.questionsAsked'), value: feedback.questions_asked ?? 0, icon: 'Message' },
    { key: t('stats.sessionLength'), value: feedback.session_length_s ?? 0, icon: 'Clock' },
    { key: t('stats.goalsAchieved'), value: feedback.goals_achieved ?? 0, icon: 'Check' },
  ];

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
  return (
    <div className="flex flex-col items-center gap-7 mx-auto max-w-3xl">
      <div className="text-2xl ">{t('title')}</div>
      <div className="h-20 bg-marigold-10 px-4 py-5 rounded-md text-center w-full">
        <div className="text-lg text-marigold-90">{feedback.session_id}</div>
        <div className="text-base text-marigold-95">{feedback.created_at}</div>
      </div>
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
          {feedback.overall_score}%
        </div>
      </div>
      <div className="my-4 mx-2 h-px w-full bg-bw-30" />

      <div className="grid grid-cols-2 gap-y-4 w-full px-1 md:flex md:justify-between">
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
              <span>{feedback.session_length_s} min</span>
            </div>
          </div>
        </div>
      </div>
      <Button variant="outline" size="full">
        {t('yourApproach')}
      </Button>
      <Accordion type="multiple" className="w-full">
        <AccordionItem value="feedback">
          <AccordionTrigger>{t('accordian.feedback')}</AccordionTrigger>
          <AccordionContent className="px-5">
            <div className="flex items-center gap-2 mt-3">
              <CheckCircle size={24} className="text-forest-50" />
              <span className="text-xl">{t('detailedFeedback.positive')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {Array.isArray(feedback.example_positive) &&
                feedback.example_positive.map((example, index) => (
                  <FeedbackQuote key={index} {...example} icon="Check" />
                ))}
            </div>

            <div className="flex items-center gap-2 mt-10">
              <CircleX size={24} className="text-flame-50" />
              <span className="text-xl">{t('detailedFeedback.negative')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {Array.isArray(feedback.example_negative) &&
                feedback.example_negative.map((negative, index) => (
                  <FeedbackQuote key={index} {...negative} icon="Cross" />
                ))}
            </div>

            <div className="flex items-center gap-2 mt-10">
              <ChartNoAxesColumnIncreasingIcon size={24} className="text-marigold-50" />
              <span className="text-xl">{t('detailedFeedback.recommendations')}</span>
            </div>
            <div className="flex flex-col gap-4 mt-5 pl-4">
              {Array.isArray(feedback.recommendations) &&
                feedback.recommendations.map((recommendation, index) => (
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
      <Link href="/dashboard" className="w-full">
        <Button size="full">{t('return')}</Button>
      </Link>
    </div>
  );
}
