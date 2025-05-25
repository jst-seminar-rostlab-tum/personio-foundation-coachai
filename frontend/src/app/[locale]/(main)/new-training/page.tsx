import type { Metadata } from 'next';
import NewTrainingForm from '@/components/layout/NewTrainingForm';

export const metadata: Metadata = {
  title: 'CoachAI - New Training',
  description: 'Start a new training session with personalized coaching',
};

export default function NewTrainingPage() {
  return <NewTrainingForm />;
}
