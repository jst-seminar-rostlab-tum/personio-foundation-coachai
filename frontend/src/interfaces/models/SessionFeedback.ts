import { SessionScores } from './Common';

export interface FeedbackResponse {
  id: string;
  scenarioId: string;
  title: string;
  createdAt: string;
  feedback?: SessionFeedback;
  goalsTotal: string[];
  hasReviewed: boolean;
}

export interface SessionFeedback {
  scores: SessionScores;
  overallScore: number;
  sessionLengthS: number;
  goalsAchieved: string[];
  documentNames: string[];
  fullAudioUrl: string;
  examplePositive: {
    heading: string;
    feedback: string;
    quote: string;
  }[];
  exampleNegative: {
    heading: string;
    feedback: string;
    quote: string;
    improvedQuote: string;
  }[];
  recommendations: {
    heading: string;
    recommendation: string;
  }[];
}
