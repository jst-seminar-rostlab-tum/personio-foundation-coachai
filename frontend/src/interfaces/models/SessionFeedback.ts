import { SessionScores } from './Common';

export interface FeedbackResponse {
  title: string;
  createdAt: string;
  feedback?: SessionFeedback;
  goalsTotal: string[];
}

export interface SessionFeedback {
  scores: SessionScores;
  overallScore: number;
  sessionLengthS: number;
  goalsAchieved: string[];
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
