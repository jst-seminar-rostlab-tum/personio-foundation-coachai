'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronDown } from 'lucide-react';
import { ClickableTable, ClickableTableColumn } from '@/components/common/ClickableTable';
import { DeleteConfirmButton } from '@/components/common/DeleteConfirmButton';
import { Session } from '@/interfaces/models/Session';
import { sessionService } from '@/services/SessionService';
import { api } from '@/services/ApiClient';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { Button } from '@/components/ui/Button';
import { useLocale, useTranslations } from 'next-intl';
import { formatDateFlexible } from '@/lib/utils/formatDateAndTime';
import EmptyListComponent from '@/components/common/EmptyListComponent';

export default function HistoryTable({
  sessions,
  limit,
  totalSessions,
  scenarioId,
}: {
  sessions: Session[];
  limit: number;
  totalSessions: number;
  scenarioId: string;
}) {
  const tCommon = useTranslations('Common');
  const tHistory = useTranslations('History');
  const locale = useLocale();
  const router = useRouter();
  const [rows, setRows] = useState(sessions);
  const [isLoading, setIsLoading] = useState(false);
  const [pageNumber, setPageNumber] = useState(1);
  const [visibleCount, setVisibleCount] = useState(limit);
  const canLoadMore = visibleCount < totalSessions;

  const handleLoadMore = (newPage: number) => {
    setPageNumber(newPage);
  };

  const getSessions = async () => {
    try {
      setIsLoading(true);
      const response = await sessionService.getPaginatedSessions(
        api,
        pageNumber,
        limit,
        scenarioId
      );
      setRows((prev) => [...prev, ...response.data.sessions]);
      setVisibleCount((prev) => prev + limit);
    } catch (e) {
      showErrorToast(e, tCommon('error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRowClick = (row: Session) => router.push(`/feedback/${row.sessionId}`);

  const handleDelete = async (id: string) => {
    try {
      await sessionService.deleteSession(api, id);
      setRows((prev) => prev.filter((row) => row.sessionId !== id));
      await getSessions();
      showSuccessToast(tHistory('deleteSessionSuccess'));
    } catch (error) {
      showErrorToast(error, tHistory('deleteSessionError'));
    }
  };

  useEffect(() => {
    if (canLoadMore && pageNumber > 1) {
      getSessions();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageNumber, canLoadMore, limit, tCommon]);

  const columns: ClickableTableColumn<(typeof rows)[number]>[] = [
    {
      header: tHistory('duration'),
      accessor: 'sessionLengthS',
      cell: (row) => {
        const minutes = Math.floor(row.sessionLengthS / 60);
        const seconds = row.sessionLengthS % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')} min`;
      },
    },
    {
      header: tHistory('sessionTime'),
      accessor: 'date',
      cell: (row) => formatDateFlexible(row.date, locale, true),
    },

    {
      header: tHistory('performance'),
      accessor: 'overallScore',
    },
    {
      header: '',
      accessor: () => '',
      className: 'text-right',
      cell: (row) => <DeleteConfirmButton onConfirm={() => handleDelete(row.sessionId)} />,
    },
  ];

  if (!rows.length) {
    return <EmptyListComponent itemType="session" />;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 max-w-full">
      <ClickableTable
        columns={columns}
        data={rows}
        onRowClick={handleRowClick}
        rowKey={(row) => row.sessionId}
      />
      {canLoadMore && (
        <div className="flex justify-center mt-4 mb-4">
          <Button variant="ghost" onClick={() => handleLoadMore(pageNumber + 1)}>
            {isLoading ? tCommon('loading') : tCommon('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
