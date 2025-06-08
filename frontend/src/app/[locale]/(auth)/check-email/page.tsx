import { MetadataProps } from '@/interfaces/MetadataProps';
import { Metadata } from 'next';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import { useTranslations } from 'next-intl';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/check-email', true);
}

export default function CheckEmailPage() {
  const t = useTranslations('CheckEmail');

  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8 text-center">
          <h1 className="text-2xl font-bold mb-2">{t('checkEmail')}</h1>
          <p className="text-gray-600 mb-6">{t('confirmationSent')}</p>
          <p className="text-sm text-gray-400">{t('spamFolderNote')}</p>
        </div>
      </div>
    </div>
  );
}
