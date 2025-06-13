'use client';

import { ChevronDown, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';
import { useTranslations } from 'next-intl';
import HistoryItem from '@/components/common/HistoryItem';

const mockSessions = [
  {
    title: 'Negotiating Job Offers',
    description: 'Practice salary negotiation with a potential candidate',
    date: '2025-06-10T09:15:00',
    duration: 1728,
  },
  {
    title: 'Conflict Resolution',
    description: 'Mediate a disagreement between team members',
    date: '2025-06-09T14:00:00',
    duration: 2925,
  },
  {
    title: 'Performance Review',
    description: 'Conduct a quarterly performance review',
    date: '2025-06-08T10:30:00',
    duration: 1263,
  },
  {
    title: 'Team Building',
    description: 'Facilitate a team building exercise',
    date: '2025-06-06T16:45:00',
    duration: 3287,
  },
  {
    title: 'Feedback Session',
    description: 'Give constructive feedback to a peer',
    date: '2025-06-05T08:00:00',
    duration: 528,
  },
  {
    title: 'Project Kickoff',
    description: 'Start a new project with the team',
    date: '2025-06-03T13:00:00',
    duration: 3537,
  },
  {
    title: 'One-on-One',
    description: 'Have a one-on-one meeting with a direct report',
    date: '2025-06-02T11:20:00',
    duration: 1323,
  },
  {
    title: 'Strategy Planning',
    description: 'Plan the strategy for the next quarter',
    date: '2025-06-01T15:30:00',
    duration: 1724,
  },
];

export default function PreviousSessions() {
  const [visibleCount, setVisibleCount] = useState(3);
  const t = useTranslations('History');

  const visibleSessions = mockSessions.slice(0, visibleCount);
  const canLoadMore = visibleCount < mockSessions.length;

  const handleLoadMore = () => {
    setVisibleCount((prev) => Math.min(prev + 3, mockSessions.length));
  };

  return (
    <div className="w-full mx-auto mt-10 px-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2 gap-2 md:gap-0">
        <div className="text-xl">{t('previousSessions')}</div>
        <div className="flex justify-between md:gap-6">
          <Button variant="ghost">
            {t('exportHistory')} <Download />
          </Button>
          <Button variant="ghost" className="hover:text-flame-50">
            {t('clearAll')} <Trash2 />
          </Button>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        {visibleSessions.map((session, idx) => (
          <HistoryItem
            key={idx}
            title={session.title}
            description={session.description}
            date={new Date(session.date)}
            duration={session.duration}
          />
        ))}
      </div>
      {canLoadMore && (
        <div className="flex justify-center mt-4">
          <Button variant="ghost" onClick={handleLoadMore}>
            {t('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
