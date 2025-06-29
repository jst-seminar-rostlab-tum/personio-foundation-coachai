export interface FeedbackResponse {
  title: string;
  createdAt: string;
  feedback?: SessionFeedback;
  goalsTotal: string[];
}

export interface SessionScores {
  clarity: number;
  empathy: number;
  structure: number;
  focus: number;
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
