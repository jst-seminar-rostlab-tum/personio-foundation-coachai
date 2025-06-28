import Image from 'next/image';
import { useTranslations } from 'next-intl';
import { EmptyListComponentProps } from '@/interfaces/EmptyListComponentProps';

export default function EmptyListComponent({ itemType }: EmptyListComponentProps) {
  const t = useTranslations('Common.emptyList');
  return (
    <div className="flex flex-col items-center justify-center w-full border border-bw-20 rounded-lg bg-transparent gap-1 p-8 text-center">
      <Image
        src="/images/common/empty-list.png"
        alt="Empty list illustration"
        width={128}
        height={128}
        className="mb-4"
      />
      <h3 className="text-xl font-semibold text-bw-90 capitalize">{t('title', { itemType })}</h3>
      <p className="text-base text-bw-40">{t('description', { itemType })}</p>
    </div>
  );
}
