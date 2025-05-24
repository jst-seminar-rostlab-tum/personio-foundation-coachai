import { UserPreference } from '@/interfaces/UserInputFields';

export const userPreferences: UserPreference[] = [
  {
    label: 'Preferred Language',
    options: [
      { code: 'en', name: 'English' },
      { code: 'es', name: 'Spanish' },
      { code: 'fr', name: 'French' },
    ],
    defaultValue: 'en',
  },
  {
    label: 'Preferred Learning Style',
    options: [
      { code: 'visual', name: 'Visual' },
      { code: 'hands-on', name: 'Hands-on practice' },
      { code: 'auditory', name: 'Auditory' },
      { code: 'kinesthetic', name: 'Kinesthetic' },
    ],
    defaultValue: 'hands-on',
  },
  {
    label: 'Preferred Session',
    options: [
      { code: 'short', name: 'Less than 30 minutes' },
      { code: 'medium', name: '30–60 minutes' },
      { code: 'long', name: 'Over 1 hour' },
    ],
    defaultValue: 'medium',
  },
];
