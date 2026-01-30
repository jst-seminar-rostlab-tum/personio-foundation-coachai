import { SessionScores } from './Common';
import { Document } from './Document';

/**
 * Response payload for session feedback details.
 */
export interface FeedbackResponse {
  id: string;
  scenarioId: string;
  title: string;
  createdAt: string;
  feedback?: SessionFeedback;
  goalsTotal: string[];
  hasReviewed: boolean;
}

/**
 * Detailed feedback content for a session.
 */
export interface SessionFeedback {
  scores: SessionScores;
  overallScore: number;
  sessionLengthS: number;
  goalsAchieved: string[];
  documents: Document[];
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
