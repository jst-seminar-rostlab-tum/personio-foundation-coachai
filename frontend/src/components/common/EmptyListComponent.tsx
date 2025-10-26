'use client';

import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface EmptyListComponentProps {
  itemType: string;
  showBorder?: boolean;
}

export default function EmptyListComponent({
  itemType,
  showBorder = true,
}: EmptyListComponentProps) {
  const t = useTranslations('Common.emptyList');
  return (
    <div
      className={`flex flex-col items-center justify-center w-full rounded-lg bg-custom-beige gap-1 p-8 text-center ${
        showBorder ? 'border border-bw-40' : ''
      }`}
    >
      <Image
        src="/images/common/empty-list.png"
        alt="Empty list illustration"
        width={128}
        height={128}
        className="mb-4"
      />
      <h3 className="text-xl font-semibold text-bw-90 capitalize">{t('title', { itemType })}</h3>
      <p className="text-base text-bw-70">{t('description', { itemType })}</p>
    </div>
  );
}
