import Link from 'next/link';
import Image from 'next/image';
import { MessageSquare, BrainCircuit, TrendingUp, Target } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { getTranslations } from 'next-intl/server';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import type { Metadata } from 'next';
import { HighlightedAppName } from '@/components/common/HighlightedAppName';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '', false);
}

export default async function AboutPage() {
  const t = await getTranslations('HomePage');
  const howItWorks = [
    {
      number: 1,
      title: t('howItWorks.steps.1.title'),
      description: t('howItWorks.steps.1.description'),
    },
    {
      number: 2,
      title: t('howItWorks.steps.2.title'),
      description: t('howItWorks.steps.2.description'),
    },
    {
      number: 3,
      title: t('howItWorks.steps.3.title'),
      description: t('howItWorks.steps.3.description'),
    },
  ];
  const features = [
    {
      icon: MessageSquare,
      title: t('features.items.sessions.title'),
      description: t('features.items.sessions.description'),
    },
    {
      icon: BrainCircuit,
      title: t('features.items.feedback.title'),
      description: t('features.items.feedback.description'),
    },
    {
      icon: TrendingUp,
      title: t('features.items.progress.title'),
      description: t('features.items.progress.description'),
    },
    {
      icon: Target,
      title: t('features.items.personalized.title'),
      description: t('features.items.personalized.description'),
    },
  ];
  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex-1">
        <section className="pb-16 lg:pt-20 md:pb-24 bg-gradient-to-br to-primary/5">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-marigold-30/80 text-primary text-sm font-medium shadow-sm">
                {t('hero.badge')}
              </div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-black leading-tight">
                {t('hero.title')}
              </h1>
              <p className="text-md md:text-xl text-black/60 font-medium">
                {t('hero.description')}
              </p>
              <div className="flex flex-col lg:flex-row gap-4 w-full">
                <Button asChild variant="default" className="w-full md:w-auto text-center">
                  <Link href="/login" className="w-full md:w-auto">
                    {t('getStarted')}
                  </Link>
                </Button>
                <Button asChild variant="outline" className="w-full md:w-auto text-center">
                  <Link href="#how-it-works" className="w-full md:w-auto">
                    {t('hero.cta.secondary')}
                  </Link>
                </Button>
              </div>
            </div>
            <div className="rounded-xl overflow-hidden shadow-lg">
              <div className="w-full aspect-[16/9] md:h-96 bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                <Image
                  src="/images/hero.jpg"
                  alt="Hero Image"
                  width={1280}
                  height={896}
                  className="w-full h-full object-cover"
                  priority
                />
              </div>
            </div>
          </div>
        </section>
        <section className="py-8 md:py-20 border-b border-t border-black/10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <p className="text-md md:text-xl font-medium">{t('developedBy')}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <a href="https://www.csee.tech/" target="_blank" rel="noopener noreferrer">
              <Image
                src="/images/logos/csee.png"
                alt="CSEE"
                width={300}
                height={85}
                className="mx-auto"
              />
            </a>
            <a href="https://www.personio.foundation/" target="_blank" rel="noopener noreferrer">
              <Image
                src="/images/logos/personio-foundation.svg"
                alt="Personio Foundation"
                width={300}
                height={85}
                className="mx-auto"
              />
            </a>
          </div>
        </section>

        <section id="how-it-works" className="scroll-mt-10 py-8 md:py-20">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-2xl md:text-3xl font-bold text-black mb-4">
              {t.rich('howItWorks.title', { appName: () => <HighlightedAppName /> })}
            </h2>
            <p className="text-md md:text-xl text-black/60 font-medium">
              {t('howItWorks.description')}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {howItWorks.map((step) => (
              <div key={step.number} className="flex flex-col items-center text-center p-6">
                <div className="w-16 h-16 rounded-full bg-black text-white flex items-center justify-center text-xl font-bold mb-6">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold text-black mb-3">{step.title}</h3>
                <p className="text-black/60">{step.description}</p>
              </div>
            ))}
          </div>

          <div className="w-full mt-8">
            <Link href="/login" className="inline-flex items-center justify-center w-full">
              <Button variant="default" className="w-full md:w-auto">
                {t('howItWorks.cta')}
              </Button>
            </Link>
          </div>
        </section>

        <section className="py-8 md:py-20 ">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-2xl md:text-3xl font-bold text-black mb-4">
              {t('features.title')}
            </h2>
            <p className="text-md md:text-xl text-black/60 font-medium">
              {t('features.description')}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2  gap-8">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-xl border-none bg-white shadow-sm transition-all hover:shadow-md"
              >
                <div className="w-12 h-12 rounded-lg bg-marigold-30/50 flex items-center justify-center text-marigold-90 mb-4">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-black mb-2">{feature.title}</h3>
                <p className="text-black/60">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="pb-18 pt-8 md:pt-16 md:pb-20">
          <div className="text-center max-w-3xl mx-auto w-full">
            <h2 className="text-2xl md:text-3xl font-bold text-black mb-4">{t('cta.title')}</h2>
            <p className="text-md md:text-xl text-black/60 mb-8 font-medium">
              {t('cta.description')}
            </p>
            <div className="w-full">
              <Link href="/login" className="inline-flex items-center justify-center w-full">
                <Button variant="default" className="w-full md:w-auto">
                  {t('getStarted')}
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
