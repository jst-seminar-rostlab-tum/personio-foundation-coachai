'use client';

import { ChevronDown, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';
import { useTranslations } from 'next-intl';

const mockSessions = [
  {
    title: 'Negotiating Job Offers',
    description: 'Practice salary negotiation with a potential candidate',
    date: '16.04.25',
    time: '12:37',
  },
  {
    title: 'Conflict Resolution',
    description: 'Mediate a disagreement between team members',
    date: '08.04.25',
    time: '13:36',
  },
  {
    title: 'Performance Review',
    description: 'Conduct a quaterly performance review',
    date: '16.04.25',
    time: '12:37',
  },
  {
    title: 'Team Building',
    description: 'Facilitate a team building exercise',
    date: '07.03.25',
    time: '10:15',
  },
  {
    title: 'Feedback Session',
    description: 'Give constructive feedback to a peer',
    date: '22.02.25',
    time: '09:00',
  },
  {
    title: 'Project Kickoff',
    description: 'Start a new project with the team',
    date: '15.01.25',
    time: '14:20',
  },
  {
    title: 'One-on-One',
    description: 'Have a one-on-one meeting with a direct report',
    date: '10.01.25',
    time: '11:45',
  },
  {
    title: 'Strategy Planning',
    description: 'Plan the strategy for the next quarter',
    date: '05.01.25',
    time: '16:00',
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
    <div className="w-full">
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
          <div
            key={idx}
            className=" border border-bw-20 rounded-xl px-4 py-3 flex justify-between items-center"
          >
            <div>
              <div className="font-semibold text-bw-70 text-sm mb-1">{session.title}</div>
              <div className="text-xs text-bw-40 leading-tight">{session.description}</div>
            </div>
            <div className="text-xs text-bw-70 text-center whitespace-nowrap ml-4">
              {session.date}
              <br />
              {session.time}
            </div>
          </div>
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
