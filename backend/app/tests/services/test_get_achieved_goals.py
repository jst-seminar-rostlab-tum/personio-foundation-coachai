import os
import unittest

from app.models.language import LanguageCode
from app.schemas.session_feedback import GoalsAchievedCreate, GoalsAchievedRead
from app.services.session_feedback.session_feedback_llm import get_achieved_goals


@unittest.skipUnless(os.environ.get('RUN_AI_TESTS') == 'true', 'AI test not enabled')
class TestGetAchievedGoals(unittest.TestCase):
    def setUp(self) -> None:
        self.base_objectives = [
            'Bring clarity to the situation',
            'Maintain professionalism',
            'Encourage open dialogue',
        ]
        self.language_code = LanguageCode.en

    def print_goals_stats(self, tag: str, result: GoalsAchievedRead) -> None:
        print(
            f'[{tag}] achieved={len(result.goals_achieved)} goals_achieved={result.goals_achieved}'
        )

    def test_only_clearly_demonstrated_goals_achieved(self) -> None:
        transcript = (
            'User: I want to make sure we are clear about the next steps.\n'
            "User: Let's keep this professional."
        )
        req = GoalsAchievedCreate(
            transcript=transcript,
            objectives=self.base_objectives,
            language_code=self.language_code,
        )
        result = get_achieved_goals(req)
        self.print_goals_stats('only_clearly_demonstrated_goals_achieved', result)
        self.assertSetEqual(
            set(result.goals_achieved),
            {'Bring clarity to the situation', 'Maintain professionalism'},
        )

    def test_no_goals_achieved_if_none_addressed(self) -> None:
        req = GoalsAchievedCreate(
            transcript='User: Hello, how are you?\nUser: Nice weather today!',
            objectives=['Provide feedback', 'Set clear goals'],
            language_code=self.language_code,
        )
        result = get_achieved_goals(req)
        self.print_goals_stats('no_goals_achieved_if_none_addressed', result)
        self.assertEqual(result.goals_achieved, [])

    def test_all_goals_achieved(self) -> None:
        transcript = (
            'User: I want to make sure we are clear about the next steps.\n'
            "User: Let's keep this professional.\n"
            'User: Please share your thoughts.'
        )
        req = GoalsAchievedCreate(
            transcript=transcript,
            objectives=self.base_objectives,
            language_code=self.language_code,
        )
        result = get_achieved_goals(req)
        self.print_goals_stats('all_goals_achieved', result)
        self.assertSetEqual(set(result.goals_achieved), set(self.base_objectives))

    def test_partial_achievement_subset(self) -> None:
        req = GoalsAchievedCreate(
            transcript="User: Let's keep this professional.",
            objectives=self.base_objectives,
            language_code=self.language_code,
        )
        result = get_achieved_goals(req)
        self.print_goals_stats('partial_achievement_subset', result)
        self.assertEqual(result.goals_achieved, ['Maintain professionalism'])

    def test_only_assistant_or_empty_transcript(self) -> None:
        for transcript in ['Assistant: Please share your thoughts.', '']:
            req = GoalsAchievedCreate(
                transcript=transcript,
                objectives=self.base_objectives,
                language_code=self.language_code,
            )
            result = get_achieved_goals(req)
            self.print_goals_stats('only_assistant_or_empty_transcript', result)
            self.assertEqual(result.goals_achieved, [])

    def test_get_achieved_goals_with_various_audios(self) -> None:
        from app.connections.gcs_client import get_gcs_audio_manager

        audio_files = ['standard.mp3', 'playful.mp3', 'excited.mp3', 'strong_expressive.mp3']
        req = GoalsAchievedCreate(
            transcript='User: Hello',
            objectives=self.base_objectives,
            language_code=self.language_code,
        )
        for audio_file in audio_files:
            audio_uri = get_gcs_audio_manager().generate_signed_url(audio_file)
            print(f'\n==== Testing with audio: {audio_file} ====')
            try:
                result = get_achieved_goals(req, audio_uri=audio_uri)
                print(result.model_dump_json(indent=2))
            except Exception as e:
                print(f'Error with {audio_file}: {e}')


if __name__ == '__main__':
    unittest.main()
