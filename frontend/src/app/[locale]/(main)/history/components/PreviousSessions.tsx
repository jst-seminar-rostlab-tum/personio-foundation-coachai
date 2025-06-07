'use client';

import { ChevronDown, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/AlertDialog';
import { Alert, AlertDescription } from '@/components/ui/Alert';
import api from '@/services/Api';

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
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const t = useTranslations('History');

  const visibleSessions = mockSessions.slice(0, visibleCount);
  const canLoadMore = visibleCount < mockSessions.length;

  const handleLoadMore = () => {
    setVisibleCount((prev) => Math.min(prev + 3, mockSessions.length));
  };

  const handleDeleteAll = async () => {
    try {
      setIsDeleting(true);
      setError(null);
      // TODO: Get user auth context in future
      const userId = '0b222f0b-c7e5-4140-9049-35620fee8009'; // TODO: Remove this after getting auth context
      if (!userId) {
        throw new Error('User ID not found');
      }
      const response = await api.delete(`/training-session/clear-all/${userId}`);
      if (response.status === 200) {
        setVisibleCount(0);
        // TODO: Reset the sessions state in future
      } else {
        throw new Error('Failed to delete sessions');
      }
    } catch (err) {
      let errorMessage = t('deleteError');
      if (err.response) {
        switch (err.response.status) {
          case 401:
            errorMessage = t('unauthorizedError');
            break;
          case 403:
            errorMessage = t('forbiddenError');
            break;
          case 404:
            errorMessage = t('noSessionsFound');
            break;
          case 500:
            errorMessage = t('serverError');
            break;
          default:
            errorMessage = t('deleteError');
            break;
        }
      }
      setError(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="w-full mx-auto mt-10 px-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2 gap-2 md:gap-0">
        <div className="text-xl">{t('previousSessions')}</div>
        <div className="flex justify-between md:gap-6">
          <Button variant="ghost">
            {t('exportHistory')} <Download />
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="ghost" className="hover:text-flame-50" disabled={isDeleting}>
                {t('clearAll')} <Trash2 />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>{t('deleteAllConfirmTitle')}</AlertDialogTitle>
                <AlertDialogDescription>{t('deleteAllConfirmDesc')}</AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>{t('cancel')}</AlertDialogCancel>
                <AlertDialogAction onClick={handleDeleteAll} disabled={isDeleting}>
                  {isDeleting ? t('deleting') : t('confirm')}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
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
