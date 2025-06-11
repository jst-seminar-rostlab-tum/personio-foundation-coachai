'use client';

import { ChevronDown, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { getPaginatedSessions } from '@/services/SessionService';
import { Session } from '@/interfaces/Session';

export default function PreviousSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const t = useTranslations('History');

  const PAGE_SIZE = 5;

  // TODO: remove this once we have a proper auth system
  const userId = 'bcfab91c-52d0-46e0-b132-13201dddaa1a';

  // Format ISO date string to dd.MM.yy and time hh:mm
  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: '2-digit' });
  };
  const formatTime = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
  };

  const fetchSessions = async (pageNum: number) => {
    setLoading(true);
    try {
      const data = await getPaginatedSessions(userId, pageNum, PAGE_SIZE);
      setSessions((prev) => [...prev, ...data.sessions]);
      setTotalPages(data.totalPages);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // load first page
    fetchSessions(1);
  }, []);

  const handleLoadMore = () => {
    if (page < totalPages && !loading) {
      const next = page + 1;
      setPage(next);
      fetchSessions(next);
    }
  };

  const canLoadMore = page < totalPages;

  return (
    <div className="w-full mx-auto mt-10 px-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2 gap-2 md:gap-0">
        <div className="text-xl">{t('previousSessions')}</div>
        <div className="flex justify-between md:gap-6">
          <Button variant="ghost" disabled={sessions.length === 0 || loading}>
            {t('exportHistory')} <Download />
          </Button>
          <Button variant="ghost" className="hover:text-flame-50" disabled={sessions.length === 0}>
            {t('clearAll')} <Trash2 />
          </Button>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        {sessions.map((session) => (
          <div
            key={session.sessionId}
            className="border border-bw-20 rounded-xl px-4 py-3 flex justify-between items-center"
          >
            <div>
              <div className="font-semibold text-bw-70 text-sm mb-1">{session.title}</div>
              <div className="text-xs text-bw-40 leading-tight">{session.summary}</div>
            </div>
            <div className="text-xs text-bw-70 text-center whitespace-nowrap ml-4">
              {formatDate(session.date)}
              <br />
              {formatTime(session.date)}
            </div>
          </div>
        ))}
      </div>
      {canLoadMore && (
        <div className="flex justify-center mt-4">
          <Button variant="ghost" onClick={handleLoadMore} disabled={loading}>
            {loading ? t('loading') : t('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
