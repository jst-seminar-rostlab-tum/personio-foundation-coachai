'use client';

import { ChevronDown, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { clearAllSessions, sessionService } from '@/services/SessionService';
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
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { SessionPaginated, SessionFromPagination } from '@/interfaces/models/Session';
import Link from 'next/link';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { api } from '@/services/ApiClient';

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
  const [totalSessionsCount, setTotalSessionsCount] = useState(totalSessions);
  const t = useTranslations('History');
  const tCommon = useTranslations('Common');
  const canLoadMore = visibleCount < totalSessionsCount;

  const handleLoadMore = (newPage: number) => {
    setPageNumber(newPage);
  };

  useEffect(() => {
    const getSessions = async () => {
      try {
        setIsLoading(true);
        const response = await sessionService.getPaginatedSessions(api, pageNumber, limit);
        setSessionsStorage((prev) => [...prev, ...response.data.sessions]);
        setVisibleCount((prev) => prev + limit);
        setTotalSessionsCount(response.data.totalSessions);
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
      await clearAllSessions(api);

      setSessionsStorage([]);
      setTotalSessionsCount(0);

      showSuccessToast(t('deleteSuccess'));
    } catch (e) {
      showErrorToast(e, t('deleteError'));
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
            {tCommon('export')} <Download />
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
                <AlertDialogCancel>{tCommon('cancel')}</AlertDialogCancel>
                <AlertDialogAction onClick={handleDeleteAll}>{tCommon('delete')}</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        {!sessionsStorage || sessionsStorage.length === 0 ? (
          <EmptyListComponent itemType={tCommon('sessions')} />
        ) : (
          sessionsStorage.map((session: SessionFromPagination) => (
            <Link
              key={session.sessionId}
              href={`/feedback/${session.sessionId}`}
              className="border border-bw-20 rounded-xl px-4 py-3 flex justify-between items-center cursor-pointer transition-all duration-300 hover:shadow-md"
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
            </Link>
          ))
        )}
      </div>
      {canLoadMore && (
        <div className="flex justify-center mt-4">
          <Button variant="ghost" onClick={() => handleLoadMore(pageNumber + 1)}>
            {isLoading ? tCommon('loading') : tCommon('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
