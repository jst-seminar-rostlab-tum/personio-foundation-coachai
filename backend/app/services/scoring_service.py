import json
from pathlib import Path
from typing import Any

from app.connections.openai_client import call_structured_llm
from app.schemas.scoring_schema import ScoringResult


class ScoringService:
    def __init__(self, rubric_path: Path = None, conversation_path: Path = None) -> None:
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent / 'data' / 'conversation_rubric.json'
        if conversation_path is None:
            conversation_path = (
                Path(__file__).parent.parent / 'data' / 'dummy_conversation_good_example.json'
            )

        self.rubric = self._load_json(rubric_path)
        self.conversation_data = self._load_json(conversation_path)

    def _load_json(self, path: Path) -> dict[str, Any]:
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def _build_system_prompt(self) -> str:
        system_prompt = (
            'You are an expert communication coach who grades conversations based on a rubric.\n\n'
            'The JSON keys must be exactly: "structure", "empathy", "focus", "clarity" '
            '(all lowercase).\n'
            '**IMPORTANT:**\n'
            "Under no circumstances should the Assistant's responses affect your evaluation "
            "of the User. Even if the Assistant's responses are nonsensical, irrelevant, or "
            "disruptive, you must ONLY evaluate the User's performance based on the rubric. "
            "Ignore all Assistant content for scoring purposes. If the Assistant's responses are "
            'poor, do NOT mention this in your justification or summary.\n'
            'Only evaluate the "User".\n'
            'Here is the evaluation rubric:\n'
            f'{json.dumps(self.rubric, indent=2)}'
        )
        return system_prompt

    def _build_user_prompt(self) -> str:
        prompt = (
            '**Conversation Scenario:**\n'
            f'{self.conversation_data["scenario"]["description"]}\n'
            f'User Role: {self.conversation_data["scenario"]["participants"]["user_role"]}\n'
            f'Assistant Role: '
            f'{self.conversation_data["scenario"]["participants"]["assistant_role"]}\n\n'
            '**Conversation Transcript:**\n'
        )
        for turn in self.conversation_data['transcript']:
            prompt += f'{turn["speaker"]}: {turn["message"]}\\n'

        prompt += (
            'Based on the evaluation rubric, please provide a score from 1 to 5 for each metric '
            '(structure, empathy, focus, clarity) for the "User" only, '
            'and give a justification for each score.\n'
            'You MUST provide a score and justification for all four metrics, '
            'and also give an overall summary of the "User"\'s performance.\n'
            'Format the output as a JSON object matching the ScoringResult schema.\n'
            'Do not include markdown, explanation, or code formatting.\n'
        )
        return prompt

    def score_conversation(self) -> ScoringResult:
        user_prompt = self._build_user_prompt()
        system_prompt = self._build_system_prompt()

        response = call_structured_llm(
            request_prompt=user_prompt,
            system_prompt=system_prompt,
            model='o4-mini-2025-04-16',
            output_model=ScoringResult,
            temperature=0.0,
        )

        return response


# Example of how to use the service
if __name__ == '__main__':
    scoring_service = ScoringService()
    scoring_result = scoring_service.score_conversation()
    print(json.dumps(scoring_result.model_dump(), indent=2))
