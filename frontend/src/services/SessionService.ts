import { FeedbackResponse } from '@/interfaces/FeedbackQuoteProps';
import { api } from './Api';

const mockFeedback: FeedbackResponse = {
  title: 'Giving Constructive Feedback',
  createdAt: '2025-06-15T09:50:10.634Z',
  feedback: {
    scores: {
      structure: 85,
      empathy: 89,
      clarity: 89,
      solutionFocus: 91,
    },
    overallScore: 82,
    sessionLengthS: 210,
    goalsAchieved: 4,
    examplesPositive: [
      {
        heading: 'Clear framing of the issue',
        feedback:
          'You effectively communicated the specific issue (missed deadlines) and its impact on the team without being accusatory.',
        quote:
          'I’ve noticed that several deadlines were missed last week, and it’s causing our team to fall behind on the overall project timeline.',
      },
      {
        heading: 'Strong active listening',
        feedback:
          'You demonstrated excellent listening skills by paraphrasing Sarah’s concerns and asking thoughtful follow-up questions.',
        quote:
          'It sounds like you’re feeling overwhelmed by the number of tasks you’re responsible for. Let’s talk about how we might prioritize these better.',
      },
    ],
    examplesNegative: [
      {
        heading: 'More specific examples needed',
        feedback:
          'Your feedback would have been more impactful with specific examples of the missed deadlines and their consequences.',
        quote: 'Several tasks have been delayed…',
        improvedQuote:
          'The UI mockups were due last Tuesday and the API documentation was due Friday, both of which are still incomplete. This has prevented the developers from starting their work.',
      },
      {
        heading: 'Rushed to solutions',
        feedback:
          'You moved to problem-solving before fully exploring the root causes of the missed deadlines.',
        quote: '',
        improvedQuote:
          'What specific challenges have made it difficult to meet these deadlines? Are there particular aspects of these tasks that are taking more time than expected?',
      },
    ],
    recommendations: [
      {
        heading: 'Practice the STAR method',
        recommendation:
          'When giving feedback, use the Situation, Task, Action, Result framework to provide more concrete examples.',
      },
      {
        heading: 'Ask more diagnostic questions',
        recommendation:
          'Spend more time understanding root causes before moving to solutions. This builds empathy and leads to more effective outcomes.',
      },
      {
        heading: 'Define clear next steps',
        recommendation: 'End feedback conversations with agreed-upon action items.',
      },
    ],
  },
};

export const getSessionFeedback = async (
  sessionId: string,
  retries = 5,
  delay = 2000
): Promise<FeedbackResponse> => {
  try {
    const response = await api.get(`/session/${sessionId}`);

    if (response.status === 200) {
      return response.data;
    }

    if (response.status === 202) {
      if (retries === 0) {
        return mockFeedback;
      }
      await new Promise((resolve) => {
        setTimeout(resolve, delay);
      });
      return await getSessionFeedback(sessionId, retries - 1, delay);
    }

    throw new Error(`Unexpected response status: ${response.status}`);
  } catch (error) {
    console.error('Error fetching session feedback:', error);
    throw error;
  }
};
