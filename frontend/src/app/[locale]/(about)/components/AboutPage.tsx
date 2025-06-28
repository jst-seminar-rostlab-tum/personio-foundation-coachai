'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import Image from 'next/image';
import { MessageSquare, Video, BrainCircuit, TrendingUp, Award, Target } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function AboutPageComponent() {
  const t = useTranslations('HomePage');

  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex-1">
        <section className="pb-16 lg:pt-8 md:pb-24 bg-gradient-to-br from-white to-primary/5">
          <div className="container">
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
                  <Button asChild variant="secondary" className="w-full md:w-auto text-center">
                    <Link href="#how-it-works" className="w-full md:w-auto">
                      {t('hero.cta.secondary')}
                    </Link>
                  </Button>
                </div>
              </div>
              <div className="rounded-xl overflow-hidden shadow-lg">
                <div className="w-full aspect-[16/9] md:h-96 bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                  <Image
                    src="/images/hero.png"
                    alt="Hero Image"
                    width={1280}
                    height={896}
                    className="w-full h-full object-cover"
                    priority
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="scroll-mt-10 py-8 md:py-20 bg-white">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-2xl md:text-3xl font-bold text-black mb-4">
                {t('howItWorks.title')}
              </h2>
              <p className="text-md md:text-xl text-black/60 font-medium">
                {t('howItWorks.description')}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
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
              ].map((step) => (
                <div key={step.number} className="flex flex-col items-center text-center p-6">
                  <div className="w-16 h-16 rounded-full bg-marigold-30 text-marigold-90 flex items-center justify-center text-xl font-bold mb-6">
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
          </div>
        </section>

        <section className="py-8 md:py-20 ">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-2xl md:text-3xl font-bold text-black mb-4">
                {t('features.title')}
              </h2>
              <p className="text-md md:text-xl text-black/60 font-medium">
                {t('features.description')}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: MessageSquare,
                  title: t('features.items.simulations.title'),
                  description: t('features.items.simulations.description'),
                },
                {
                  icon: Video,
                  title: t('features.items.voice.title'),
                  description: t('features.items.voice.description'),
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
                  icon: Award,
                  title: t('features.items.gamification.title'),
                  description: t('features.items.gamification.description'),
                },
                {
                  icon: Target,
                  title: t('features.items.personalized.title'),
                  description: t('features.items.personalized.description'),
                },
              ].map((feature) => (
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
          </div>
        </section>

        <section className="pb-18 pt-8 md:pt-16 md:pb-20">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto w-full">
              <h2 className="text-2xl md:text-3xl font-bold text-black mb-4">{t('cta.title')}</h2>
              <p className="text-md md:text-xl text-black/60 mb-8 font-medium">
                {t('cta.description')}
              </p>
              <div className="w-full">
                <Link href="/login" className="inline-flex items-center justify-center w-full">
                  <Button variant="default" className="w-full md:w-auto">
                    {t('getStartedNow')}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
