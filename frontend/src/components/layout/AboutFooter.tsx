import Link from 'next/link';
import { getTranslations } from 'next-intl/server';

export default async function AboutFooter() {
  const t = await getTranslations('HomePage');

  return (
    <footer>
      <div className="container py-4 md:pt-8 mx-auto px-4 border-t border-marigold-90">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-xl font-semibold text-black">{t('footer.appName')}</span>
            </div>
          </div>
          <div className="md:col-span-3 flex justify-between md:justify-end gap-4 md:gap-8 text-sm">
            <Link href="/privacy" className="text-stone-500 hover:text-stone-900">
              {t('footer.links.privacy')}
            </Link>
            <Link href="/terms" className="text-stone-500 hover:text-stone-900">
              {t('footer.links.terms')}
            </Link>
            <Link href="/cookies" className="text-stone-500 hover:text-stone-900">
              {t('footer.links.cookies')}
            </Link>
          </div>
        </div>
        <div className="pt-8 text-center text-stone-500 text-sm">
          <p>{t('footer.copyright')}</p>
        </div>
      </div>
    </footer>
  );
}
