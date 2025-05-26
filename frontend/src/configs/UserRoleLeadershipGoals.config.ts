import { UserPreference } from '@/interfaces/UserInputFields';

export const userRoleLeadershipGoals: UserPreference[] = [
  {
    label: 'Current Role',
    options: [
      { code: 'tl', name: 'Team Leader' },
      { code: 'rec', name: 'Recruitment Specialist' },
      { code: 'tr', name: 'Trainee' },
    ],
    defaultValue: 'tl',
  },
  {
    label: 'Leadership Experience',
    options: [
      { code: 'strong', name: 'Strong (>3 years)' },
      { code: 'intermediate', name: 'Intermediate (1-3 years)' },
      { code: 'beginner', name: 'Beginner (0-1 years)' },
      { code: 'no', name: 'No Experience' },
    ],
    defaultValue: 'intermediate',
  },
  {
    label: 'Primary Goals',
    options: [
      { code: 'feedback', name: 'Give Constructive Feedback' },
      { code: 'coaching', name: 'Coaching & Mentoring' },
      { code: 'coping', name: 'Coping Mechanisms' },
    ],
    defaultValue: 'coaching',
  },
];
