import { UserConfidenceField } from '@/interfaces/UserInputFields';

export const confidenceFields: UserConfidenceField[] = [
  {
    title: 'Giving difficult feedback',
    minLabel: 'Not confident',
    maxLabel: 'Very confident',
    minValue: 0,
    maxValue: 100,
  },
  {
    title: 'Managing team conflicts',
    minLabel: 'Not confident',
    maxLabel: 'Very confident',
    minValue: 0,
    maxValue: 100,
  },
  {
    title: 'Leading challenging conversations',
    minLabel: 'Not confident',
    maxLabel: 'Very confident',
    minValue: 0,
    maxValue: 100,
  },
];
