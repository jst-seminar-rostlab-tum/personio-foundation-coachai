# ruff: noqa: E501
import os
import string
import unittest

from app.models.language import LanguageCode
from app.schemas.session_feedback import FeedbackCreate, SessionExamplesRead
from app.services.session_feedback.session_feedback_llm import generate_training_examples


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestGenerateTrainingExamplesIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.base_feedback_request = FeedbackCreate(
            transcript='',
            objectives=['Improve communication skills', 'Build good relationships'],
            category='Feedback',
            persona='**Name**: John\n**Training Focus**: Receiving feedback',
            situational_facts='Team project feedback meeting',
            key_concepts='Active listening, constructive feedback',
            language_code=LanguageCode.en,
        )

    def remove_punctuation(self, text: str) -> str:
        return text.translate(str.maketrans('', '', string.punctuation))

    def print_example_stats(self, tag: str, result: SessionExamplesRead) -> None:
        print(
            f'[{tag}] pos={len(result.positive_examples)} neg={len(result.negative_examples)} '
            f'pos_quotes={[ex.quote for ex in result.positive_examples]} '
            f'neg_quotes={[ex.quote for ex in result.negative_examples]}'
        )

    def test_quotes_only_from_user_utterances(self) -> None:
        """
        All quotes and improved_quotes must only come from User utterances (as substring, not necessarily exact match).
        """
        transcript = (
            "User: I'd like to discuss the project progress with you.\n"
            "Assistant: Sure, I'm happy to hear your thoughts.\n"
            'User: I think your work is good, but some details could be improved.\n'
            'Assistant: Thanks for your feedback, could you be more specific?\n'
            'User: Of course, we need to collaborate better.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        # Get all User utterances
        user_utterances = [
            line[len('User: ') :] for line in transcript.split('\n') if line.startswith('User: ')
        ]
        user_utterances_no_punct = [self.remove_punctuation(u) for u in user_utterances]
        for ex in result.positive_examples + result.negative_examples:
            quote_no_punct = self.remove_punctuation(ex.quote)
            self.assertTrue(
                any(quote_no_punct in u for u in user_utterances_no_punct),
                f"Quote '{ex.quote}' is not a substring of any User utterance (ignoring punctuation).",
            )
        self.print_example_stats('quotes_only_from_user_utterances', result)

    def test_at_least_one_positive_and_negative_example(self) -> None:
        """
        At least one positive and one negative example if transcript allows.
        """
        transcript = (
            "User: I'd like to discuss the project progress, I think your work is great.\n"
            'Assistant: Thank you for your feedback.\n'
            'User: But I think communication could be more frequent.\n'
            'Assistant: I understand your point.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        self.assertGreaterEqual(
            len(result.positive_examples), 1, 'Should have at least one positive example.'
        )
        self.assertGreaterEqual(
            len(result.negative_examples), 1, 'Should have at least one negative example.'
        )
        self.print_example_stats('at_least_one_positive_and_negative_example', result)

    def test_empty_transcript_returns_empty_examples(self) -> None:
        """
        Empty transcript returns empty examples.
        """
        request = self.base_feedback_request.model_copy()
        request.transcript = ''
        result = generate_training_examples(request)
        self.assertEqual(
            len(result.positive_examples), 0, 'Empty transcript should have no positive examples.'
        )
        self.assertEqual(
            len(result.negative_examples), 0, 'Empty transcript should have no negative examples.'
        )
        self.print_example_stats('empty_transcript_returns_empty_examples', result)

    def test_quote_matches_transcript_exactly(self) -> None:
        """
        Quotes must strictly match the transcript content (special chars, line breaks).
        """
        transcript = (
            "User: I'd like to discuss the project progress, including some special characters!@#$%^&*().\n"
            'Assistant: Okay.\n'
            'User: This project is really complex, needs multiple lines to describe.\n'
            'Assistant: I understand.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        expected_quotes = [
            "I'd like to discuss the project progress, including some special characters!@#$%^&*().",
            'This project is really complex, needs multiple lines to describe.',
        ]
        expected_quotes_no_punct = [self.remove_punctuation(q) for q in expected_quotes]
        for ex in result.positive_examples + result.negative_examples:
            quote_no_punct = self.remove_punctuation(ex.quote)
            self.assertIn(
                quote_no_punct,
                expected_quotes_no_punct,
                f"Quote '{ex.quote}' does not strictly match transcript content (ignoring punctuation).",
            )
        self.print_example_stats('quote_matches_transcript_exactly', result)

    def test_improved_quote_is_reasonable_improvement(self) -> None:
        """
        Improved quote must be a clear, improved version of the original quote.
        """
        transcript = (
            'User: Your work is not good.\n'
            "Assistant: I'm sorry.\n"
            'User: Forget it, never mind.\n'
            'Assistant: I understand.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        for ex in result.negative_examples:
            self.assertIsNotNone(
                ex.improved_quote, 'Negative example should have an improved quote.'
            )
            self.assertNotEqual(
                ex.quote, ex.improved_quote, 'Improved quote should differ from original quote.'
            )
            self.assertGreater(len(ex.improved_quote), 0, 'Improved quote should not be empty.')
        self.print_example_stats('improved_quote_is_reasonable_improvement', result)

    def test_only_assistant_utterances_returns_empty(self) -> None:
        """
        Transcript with only Assistant utterances returns empty results.
        """
        transcript = (
            "Assistant: Hello, I'm the assistant.\n"
            "Assistant: I'm here to help you.\n"
            'Assistant: Is there anything I can help you with?'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        self.assertEqual(
            len(result.positive_examples),
            0,
            'Only Assistant utterances should have no positive examples.',
        )
        self.assertEqual(
            len(result.negative_examples),
            0,
            'Only Assistant utterances should have no negative examples.',
        )
        self.print_example_stats('only_assistant_utterances_returns_empty', result)

    def test_maximum_three_examples_each_type(self) -> None:
        """
        At most 3 positive and 3 negative examples are returned.
        """
        transcript = (
            'User: First user utterance.\nAssistant: Assistant reply.\n'
            'User: Second user utterance.\nAssistant: Assistant reply.\n'
            'User: Third user utterance.\nAssistant: Assistant reply.\n'
            'User: Fourth user utterance.\nAssistant: Assistant reply.\n'
            'User: Fifth user utterance.\nAssistant: Assistant reply.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        self.assertLessEqual(
            len(result.positive_examples), 3, 'Positive examples should not exceed 3.'
        )
        self.assertLessEqual(
            len(result.negative_examples), 3, 'Negative examples should not exceed 3.'
        )
        self.print_example_stats('maximum_three_examples_each_type', result)

    def test_user_assistant_alternating_roles_not_confused(self) -> None:
        """
        User and Assistant alternate turns with similar content; only User utterances are extracted.
        """
        transcript = (
            "User: I'd like to discuss the project progress.\nAssistant: I'd like to discuss the project progress.\n"
            'User: Your work is great.\nAssistant: Your work is great.\n'
            'User: But communication could be improved.\nAssistant: But communication could be improved.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        user_only_quotes = [
            "I'd like to discuss the project progress.",
            'Your work is great.',
            'But communication could be improved.',
        ]
        for ex in result.positive_examples + result.negative_examples:
            self.assertIn(
                ex.quote, user_only_quotes, f"Quote '{ex.quote}' is not from User utterances."
            )
        self.print_example_stats('user_assistant_alternating_roles_not_confused', result)

    def test_mixed_language_content_preserved(self) -> None:
        """
        Mixed language content is preserved in quotes.
        """
        transcript = (
            'User: Deine Arbeit war großartig, your communication was perfect!\n'
            'Assistant: Thank you!\n'
            'User: Your work was terrible, ich bin enttäuscht..\n'
            "Assistant: I'm sorry to hear that."
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        self.assertTrue(
            any('Deine Arbeit war großartig' in ex.quote for ex in result.positive_examples),
            "Positive examples should contain 'Deine Arbeit war großartig'",
        )
        self.assertTrue(
            any('ich bin enttäuscht' in ex.quote for ex in result.negative_examples),
            "Negative examples should contain 'ich bin enttäuscht'",
        )
        self.print_example_stats('mixed_language_content_preserved', result)

    def test_objectives_related_examples_prioritized(self) -> None:
        """
        Extracted examples should cover objectives or key concepts where possible.
        """
        transcript = (
            "User: I'd like to build a better working relationship with you.\nAssistant: Good.\n"
            'User: Your technical skills are strong.\nAssistant: Thank you.\n'
            'User: We need to improve our communication skills.\nAssistant: Agreed.'
        )
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        request.objectives = ['Build good relationships', 'Improve communication skills']
        result = generate_training_examples(request)
        found_objective = any(
            'relationship' in (ex.heading.lower() + ex.feedback.lower() + ex.quote.lower())
            or 'communication' in (ex.heading.lower() + ex.feedback.lower() + ex.quote.lower())
            for ex in result.positive_examples + result.negative_examples
        )
        self.assertTrue(found_objective, 'At least one example should relate to objectives.')
        self.print_example_stats('objectives_related_examples_prioritized', result)

    def test_very_short_transcript_handling(self) -> None:
        """
        Very short transcript is handled gracefully.
        """
        transcript = 'User: OK.\nAssistant: OK.'
        request = self.base_feedback_request.model_copy()
        request.transcript = transcript
        result = generate_training_examples(request)
        self.assertIsInstance(result, type(generate_training_examples(self.base_feedback_request)))
        self.print_example_stats('very_short_transcript_handling', result)

    def test_generate_training_examples_with_various_audios(self) -> None:
        from app.connections.gcs_client import get_gcs_audio_manager

        audio_files = ['standard.mp3', 'playful.mp3', 'excited.mp3', 'strong_expressive.mp3']
        request = self.base_feedback_request.model_copy()
        request.transcript = 'User: Hello'
        for audio_file in audio_files:
            audio_uri = get_gcs_audio_manager().generate_signed_url(audio_file)
            print(f'\n==== Testing with audio: {audio_file} ====')
            try:
                result = generate_training_examples(request, audio_uri=audio_uri)
                print(result.model_dump_json(indent=2))
            except Exception as e:
                print(f'Error with {audio_file}: {e}')


if __name__ == '__main__':
    unittest.main()
