'use client';

import { ChevronDown, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { clearAllSessions } from '@/services/client/SessionService';
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
import { SessionPaginated, SessionFromPagination } from '@/interfaces/Session';
import { api } from '@/services/client/Api';
import { getPaginatedSessions } from '@/services/server/SessionService';

export default function PreviousSessions({
  limit,
  totalSessions,
  page,
  sessions,
}: SessionPaginated) {
  const [visibleCount, setVisibleCount] = useState(limit);
  const [pageNumber, setPageNumber] = useState(page);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionsStorage, setSessionsStorage] = useState<SessionFromPagination[]>(sessions);
  const t = useTranslations('History');
  const canLoadMore = visibleCount < totalSessions;

  const handleLoadMore = (newPage: number) => {
    setPageNumber(newPage);
  };

  useEffect(() => {
    const getSessions = async () => {
      try {
        setIsLoading(true);
        const response = await getPaginatedSessions(api, pageNumber, limit);
        setSessionsStorage((prev) => [...prev, ...response.data.sessions]);
        setVisibleCount((prev) => prev + limit);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    if (canLoadMore && pageNumber > 1) {
      getSessions();
    }
  }, [pageNumber, canLoadMore, limit]);
  const handleDeleteAll = async () => {
    try {
      setIsDeleting(true);
      await clearAllSessions();
      setVisibleCount(0);
    } catch (e) {
      console.error(e);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="w-full">
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
                <AlertDialogTitle>{t('deleteAllSessions')}</AlertDialogTitle>
                <AlertDialogDescription>
                  {t('deleteAllSessionsConfirmation')}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>{t('cancel')}</AlertDialogCancel>
                <AlertDialogAction onClick={handleDeleteAll}>{t('delete')}</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        {sessionsStorage.map((session: SessionFromPagination) => (
          <div
            key={session.sessionId}
            className="border border-bw-20 rounded-xl px-4 py-3 flex justify-between items-center"
          >
            <div>
              <div className="font-semibold text-bw-70 text-sm mb-1">{session.title}</div>
              <div className="text-xs text-bw-40 leading-tight">{session.summary}</div>
            </div>
            <div className="text-xs text-bw-70 text-center whitespace-nowrap ml-4">
              {session.score}%
              <br />
              {session.status}
            </div>
          </div>
        ))}
      </div>
      {canLoadMore && (
        <div className="flex justify-center mt-4">
          <Button variant="ghost" onClick={() => handleLoadMore(pageNumber + 1)}>
            {isLoading ? t('loading') : t('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
