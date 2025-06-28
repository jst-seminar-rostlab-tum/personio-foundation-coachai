import Link from 'next/link';
import { useTranslations } from 'next-intl';

export default function AboutFooter() {
  const t = useTranslations('HomePage');
  const tCommon = useTranslations('Common');

  return (
    <footer>
      <div className="container py-4 md:pt-8 mx-auto px-4 border-t border-marigold-90">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-xl font-semibold text-black">{tCommon('appName')}</span>
            </div>
          </div>
          <div className="md:col-span-3 flex justify-between md:justify-end gap-4 md:gap-8 text-sm">
            <Link href="/privacy" className="text-stone-500 hover:text-stone-900">
              {t('privacy')}
            </Link>
            <Link href="/terms" className="text-stone-500 hover:text-stone-900">
              {t('terms')}
            </Link>
            <Link href="/cookies" className="text-stone-500 hover:text-stone-900">
              {t('cookies')}
            </Link>
          </div>
        </div>
        <div className="pt-8 text-center text-stone-500 text-sm">
          <p>{t('copyright')}</p>
        </div>
      </div>
    </footer>
  );
}
