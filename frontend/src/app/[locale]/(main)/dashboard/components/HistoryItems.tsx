import EmptyListComponent from '@/components/common/EmptyListComponent';
import { Button } from '@/components/ui/Button';
import { Link } from '@/i18n/navigation';
import { SessionFromPagination, SessionPaginatedResponse } from '@/interfaces/Session';
import { ArrowRightIcon } from 'lucide-react';
import { useLocale, useTranslations } from 'next-intl';
import { use } from 'react';

interface HistoryItemsProps {
  sessionsPromise: Promise<SessionPaginatedResponse>;
}

export default function HistoryItems({ sessionsPromise }: HistoryItemsProps) {
  const t = useTranslations('Dashboard');
  const tCommon = useTranslations('Common');
  const locale = useLocale();
  const formattedDate = (date: string) => {
    return new Date(date).toLocaleDateString(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const response = use(sessionsPromise);
  const sessions = response?.data?.sessions;

  return (
    <section className="flex flex-col gap-4">
      <div>
        <h2 className="text-xl">{t('recentSessions.title')}</h2>
        <p className="text-base text-bw-40">{t('recentSessions.subtitle')}</p>
      </div>
      {!sessions || sessions.length === 0 ? (
        <EmptyListComponent itemType={tCommon('emptyList.sessions')} />
      ) : (
        <>
          {sessions.map((session: SessionFromPagination) => (
            <Link
              key={session.sessionId}
              href={`/feedback/${session.sessionId}`}
              className="border border-bw-20 rounded-lg p-8 flex justify-between items-center gap-x-8 cursor-pointer transition-all duration-300 hover:shadow-md"
            >
              <div className="flex flex-col gap-2">
                <h2 className="text-xl">{session.title}</h2>
                <p className="text-base text-bw-40">{session.summary}</p>
              </div>
              <div className="flex flex-col justify-center text-center min-w-max">
                <p className="text-base whitespace-nowrap">{formattedDate(session.date)}</p>
              </div>
            </Link>
          ))}
          <Link href="/history">
            <Button size="full">
              {t('recentSessions.cta')}
              <ArrowRightIcon />
            </Button>
          </Link>
        </>
      )}
    </section>
  );
}
