'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import Image from 'next/image';
import {
  MessageSquare,
  Video,
  BrainCircuit,
  TrendingUp,
  Award,
  Target,
  ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Page() {
  const t = useTranslations('HomePage');

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full bg-white mb-1">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-xl font-semibold text-black">{t('header.appName')}</span>
            </Link>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Button asChild variant="default">
              <Link href="/dashboard">
                <span className="text-sm">{t('header.getStarted')}</span>
              </Link>
            </Button>
          </nav>
          <div className="md:hidden">
            <Link href="/dashboard">
              <button className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-8 w-8 bg-marigold-30">
                <ArrowRight className="h-5 w-5" />
              </button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <section className="pb-16 pt-8 md:pt-16 md:pb-24 bg-gradient-to-br from-white to-primary/5">
          <div className="container">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
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
                <div className="flex flex-col sm:flex-row gap-4 w-full">
                  <Button asChild variant="default" className="w-full md:w-auto text-center">
                    <Link href="/dashboard" className="w-full md:w-auto">
                      {t('hero.cta.primary')}
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
                <div className="w-full h-56 md:h-96 bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
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

        <section id="how-it-works" className="py-8 md:py-20 bg-white">
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
              <Link href="/new-training" className="inline-flex items-center justify-center w-full">
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
                <Link href="/dashboard" className="inline-flex items-center justify-center w-full">
                  <Button variant="default" className="w-full md:w-auto">
                    {t('cta.button')}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-marigold-90">
        <div className="container py-4 md:pt-8">
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
    </div>
  );
}
