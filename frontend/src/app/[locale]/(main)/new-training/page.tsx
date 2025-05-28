import NewTrainingForm from '@/components/common/NewTrainingForm';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'CoachAI - New Training',
  description: 'Start a new training session with personalized coaching',
};

export default function NewTrainingPage() {
  return <NewTrainingForm />;
}
