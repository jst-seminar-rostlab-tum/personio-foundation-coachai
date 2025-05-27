import type { Metadata } from 'next';
import TrainingSettingsClient from './TrainingSettingsClient';

export const metadata: Metadata = {
  title: 'CoachAI - Training Settings',
  description: 'Customize your training preferences and goals',
};

export default function TrainingSettingsPage() {
  return (
    <div className="max-w-4xl mx-auto container">
      <TrainingSettingsClient />
    </div>
  );
}
