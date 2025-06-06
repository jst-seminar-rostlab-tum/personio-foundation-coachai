import { HistoryItemProps } from '@/interfaces/HistoryItemProps';

function formatDuration(durationInSeconds: number): string {
  const hours = Math.floor(durationInSeconds / 3600);
  const minutes = Math.floor((durationInSeconds % 3600) / 60);
  const seconds = durationInSeconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }

  return `${seconds}s`;
}

export default function HistoryItem({ title, description, date, duration }: HistoryItemProps) {
  const formattedDate = date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
  });

  const formattedDuration = formatDuration(duration);

  return (
    <div className="border border-bw-20 rounded-lg p-8 flex justify-between items-center gap-x-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-xl">{title}</h2>
        <p className="text-base text-bw-40">{description}</p>
      </div>
      <div className="flex flex-col justify-center text-center min-w-max">
        <p className="text-base font-semibold whitespace-nowrap">{formattedDuration}</p>
        <p className="text-base whitespace-nowrap">{formattedDate}</p>
      </div>
    </div>
  );
}
