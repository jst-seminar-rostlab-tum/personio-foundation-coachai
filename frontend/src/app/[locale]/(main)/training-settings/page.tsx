import type { Metadata } from 'next';
import TrainingSettingsClient from './TrainingSettingsClient';

export const metadata: Metadata = {
  title: 'CoachAI - Training Settings',
  description: 'Customize your training preferences and goals',
};

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/training-settings', true);
}

export default function TrainingSettingsPage() {
  return (
    <div className="max-w-4xl mx-auto container">
      <TrainingSettingsClient />
    </div>
  );
}
