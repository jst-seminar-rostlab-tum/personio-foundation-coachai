import OnboardingLayout from '@/components/layout/OnboardingLayout';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'CoachAI - Onboarding',
  description: 'Get started with CoachAI - Set up your profile and preferences',
};

export default function OnboardingPage() {
  return <OnboardingLayout />;
}
