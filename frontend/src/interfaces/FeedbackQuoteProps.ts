export interface FeedbackQuoteProps {
  heading: string;
  feedback?: string;
  quote?: string;
  improvedQuote?: string;
  recommendation?: string;
  icon?: string;
}

export interface FeedbackResponse {
  title: string;
  createdAt: string;
  feedback?: SessionFeedback;
}

export interface SessionFeedback {
  scores: {
    clarity: number;
    empathy: number;
    structure: number;
    focus: number;
  };
  overallScore: number;
  sessionLengthS: number;
  goalsAchieved: number;
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

export interface FeedbackPageProps {
  params: Promise<{ id: string }>;
}
