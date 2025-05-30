import { useTranslations } from 'next-intl';
import {
  CheckCircle,
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
import Link from 'next/link';

const mockFeedback = {
  topic: 'Giving Constructive Feedback',
  time: '16.04.2025, 12:24',
  structure: 85,
  empathy: 85,
  focus: 85,
  overall: 82,
  speakingTime: 62,
  questionAsked: 6,
  sessionLength: '3:30',
  goalsAcheived: '4/5',
  conversationLength: 3,
};

export default function FeedbackDetail() {
  const t = useTranslations('Feedback');
  const progressBarData = [
    { key: t('progressBars.structure'), value: mockFeedback.structure },
    { key: t('progressBars.empathy'), value: mockFeedback.empathy },
    { key: t('progressBars.focus'), value: mockFeedback.focus },
  ];

  const roundCardStats = [
    { key: t('stats.speakingTime'), value: `${mockFeedback.speakingTime}%`, icon: 'Mic' },
    { key: t('stats.questionsAsked'), value: mockFeedback.questionAsked, icon: 'Message' },
    { key: t('stats.sessionLength'), value: mockFeedback.sessionLength, icon: 'Clock' },
    { key: t('stats.goalsAchieved'), value: mockFeedback.goalsAcheived, icon: 'Check' },
  ];

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'Mic':
        return <Mic size={20} />;
      case 'Message':
        return <MessageCircle size={20} />;
      case 'Clock':
        return <Clock size={20} />;
      case 'Check':
        return <CheckCircle size={20} />;
      default:
        return <MessageCircleQuestion size={20} />;
    }
  };
  return (
    <div className="flex flex-col items-center gap-7 mx-auto max-w-3xl">
      <div className="text-2xl ">{t('title')}</div>
      <div className="h-20 bg-marigold-10 px-4 py-5 rounded-md text-center w-full">
        <div className="text-lg text-marigold-90">{mockFeedback.topic}</div>
        <div className="text-base text-marigold-95">{mockFeedback.time}</div>
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
          {mockFeedback.overall}%
        </div>
      </div>
      <div className="my-4 mx-2 h-px w-full bg-bw-30" />

      <div className="grid grid-cols-2 gap-y-4 w-full md:w-fit md:gap-x-48 px-1">
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
              <span>{mockFeedback.conversationLength} min</span>
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
          <AccordionContent></AccordionContent>
        </AccordionItem>
        <AccordionItem value="suggestion">
          <AccordionTrigger>{t('accordian.suggestion')}</AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
        <AccordionItem value="session">
          <AccordionTrigger>{t('accordian.sessions')}</AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
      </Accordion>
      <Link href="/dashboard" className="w-full">
        <Button size="full">{t('return')}</Button>
      </Link>
    </div>
  );
}
