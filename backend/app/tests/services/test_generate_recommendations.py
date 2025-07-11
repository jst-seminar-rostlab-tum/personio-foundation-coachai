import os
import unittest

from app.models.language import LanguageCode
from app.schemas.session_feedback import FeedbackCreate, RecommendationsRead
from app.services.session_feedback.session_feedback_llm import generate_recommendations


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestGenerateRecommendations(unittest.TestCase):
    def setUp(self) -> None:
        self.base_objectives = [
            'Show empathy',
            'Give clear instructions',
        ]
        self.base_key_concepts = (
            'Active listening, Clear communication, Empathy, Instruction clarity'
        )
        self.language_code = LanguageCode.en

    def print_recommendations_stats(self, tag: str, result: RecommendationsRead) -> None:
        print(
            f'[{tag}] num={len(result.recommendations)} '
            f'recommendations={[rec.heading for rec in result.recommendations]}'
        )

    def test_no_recommendations_for_empty_or_assistant_only(self) -> None:
        for transcript in ['', 'Assistant: Please follow the instructions.']:
            req = FeedbackCreate(
                transcript=transcript,
                objectives=self.base_objectives,
                key_concepts='Feedback process, Communication essentials',
                category='Feedback',
                persona='Manager',
                situational_facts='Performance review',
                language_code=self.language_code,
            )
            result = generate_recommendations(req)
            self.print_recommendations_stats(
                'no_recommendations_for_empty_or_assistant_only', result
            )
            self.assertTrue(
                len(result.recommendations) == 0
                or all(
                    'no recommendation' in (rec.heading + rec.recommendation).lower()
                    for rec in result.recommendations
                )
            )

    def test_recommendations_unique_and_not_contradictory(self) -> None:
        transcript = (
            'User: You did well, but you need to improve your punctuality.\n'
            'User: Sometimes your work is late, but overall good job.'
        )
        req = FeedbackCreate(
            transcript=transcript,
            objectives=self.base_objectives,
            key_concepts='Constructive feedback, Punctuality, Positive reinforcement',
            category='Feedback',
            persona='Manager',
            situational_facts='Performance review',
            language_code=self.language_code,
        )
        result = generate_recommendations(req)
        self.print_recommendations_stats('recommendations_unique_and_not_contradictory', result)
        texts = [rec.recommendation for rec in result.recommendations]
        self.assertEqual(len(texts), len(set(texts)), 'Recommendations are not unique')

    def test_recommendations_reflect_objectives_and_key_concepts(self) -> None:
        transcript = (
            'User: I want to show more empathy in my feedback.\n'
            'User: I will try to be clearer next time.'
        )
        req = FeedbackCreate(
            transcript=transcript,
            objectives=self.base_objectives,
            key_concepts='Empathy, Clarity, Feedback improvement',
            category='Feedback',
            persona='Manager',
            situational_facts='Performance review',
            language_code=self.language_code,
        )
        result = generate_recommendations(req)
        self.print_recommendations_stats(
            'recommendations_reflect_objectives_and_key_concepts', result
        )
        found = any(
            'empathy' in (rec.heading + rec.recommendation).lower()
            or 'clarity' in (rec.heading + rec.recommendation).lower()
            for rec in result.recommendations
        )
        self.assertTrue(found, 'No recommendation reflects objectives or key concepts')

    def test_maximum_number_of_recommendations(self) -> None:
        transcript = '\n'.join([f'User: Issue {i}' for i in range(20)])
        req = FeedbackCreate(
            transcript=transcript,
            objectives=self.base_objectives,
            key_concepts='Prioritization, Focus, Actionable feedback',
            category='Feedback',
            persona='Manager',
            situational_facts='Performance review',
            language_code=self.language_code,
        )
        result = generate_recommendations(req)
        self.print_recommendations_stats('maximum_number_of_recommendations', result)
        self.assertLessEqual(len(result.recommendations), 5, 'Too many recommendations returned')


if __name__ == '__main__':
    unittest.main()
