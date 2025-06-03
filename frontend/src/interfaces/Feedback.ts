export interface FeedbackQuoteProps {
  heading: string;
  feedback?: string;
  quote?: string;
  improvedQuote?: string;
  recommendation?: string;
  icon?: string;
}

export interface FeedbackPageProps {
  params: { id: string };
}

export interface RawFeedbackData {
  id: string;
  session_id: string;
  session_topic?: string;
  overall_score: number;
  scores: {
    clarity: number;
    empathy: number;
    structure: number;
    solution_focus: number;
  };
  speak_time_percent: number;
  questions_asked: number;
  session_length_s: number;
  goals_achieved: number;
  examples_positive: {
    heading: string;
    feedback: string;
    quote: string;
  }[];
  examples_negative: {
    heading: string;
    feedback: string;
    quote: string;
    improved_quote: string;
  }[];
  recommendations: {
    heading: string;
    recommendation: string;
  }[];
  status: string;
  created_at: string;
}

export interface FeedbackData {
  sessionTopic?: string;
  overallScore: number;
  scores: {
    clarity: number;
    empathy: number;
    structure: number;
    solutionFocus: number;
  };
  speakTimePercent: number;
  questionsAsked: number;
  sessionLength: number;
  goalsAchieved: number;
  examplesPositive: {
    heading: string;
    feedback: string;
    quote: string;
  }[];
  examplesNegative: {
    heading: string;
    feedback: string;
    quote: string;
    improvedQuote: string;
  }[];
  recommendations: {
    heading: string;
    recommendation: string;
  }[];
  status: string;
  createdAt: string;
}
