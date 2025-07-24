import Link from 'next/link';
import { getTranslations } from 'next-intl/server';
import { HighlightedAppName } from '../common/HighlightedAppName';

export default async function AboutFooter() {
  const t = await getTranslations('HomePage');
  const tCommon = await getTranslations('Common');

  return (
    <footer>
      <div className="py-4 md:pt-8 mx-auto px-[clamp(1.25rem,4vw,4rem)] max-w-7xl">
        <div className="border-t border-bw-20 py-4" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-xl font-semibold text-black">
                <HighlightedAppName />
              </span>
            </div>
          </div>
          <div className="md:col-span-3 flex flex-wrap md:justify-end gap-4 md:gap-8 text-sm">
            <a
              href="https://www.csee.tech/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-stone-500 hover:text-stone-900"
            >
              {t('aboutCSEE')}
            </a>
            <a
              href="https://www.personio.foundation/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-stone-500 hover:text-stone-900"
            >
              {t('aboutPersonioFoundation')}
            </a>
            <a
              href="https://github.com/jst-seminar-rostlab-tum/personio-foundation-coachai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-stone-500 hover:text-stone-900"
            >
              GitHub
            </a>
            <Link href="/contributors" className="text-stone-500 hover:text-stone-900">
              {tCommon('contributors')}
            </Link>
            <Link href="/privacy" className="text-stone-500 hover:text-stone-900">
              {tCommon('privacyPolicy')}
            </Link>
            <Link href="/terms" className="text-stone-500 hover:text-stone-900">
              {tCommon('termsOfService')}
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
