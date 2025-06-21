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

    def _build_prompt(self) -> str:
        prompt = f"""
        You are an expert communication coach. Your task is to evaluate the "User"
        speaker in the following conversation based on the provided rubric.
        The "Assistant" speaker is an AI and should not be evaluated; their dialogue is
        for context only.

        **Rubric:**
        {json.dumps(self.rubric, indent=2)}

        **Conversation Scenario:**
        {self.conversation_data['scenario']['description']}
        User Role: {self.conversation_data['scenario']['participants']['user_role']}
        Assistant Role: {self.conversation_data['scenario']['participants']['assistant_role']}

        **Conversation Transcript:**
        """
        for turn in self.conversation_data['transcript']:
            prompt += f'{turn["speaker"]}: {turn["message"]}\\n'

        prompt += """
        Based on the rubric, please provide a score from 0-5 for each metric
        (Structure, Empathy, Focus, Clarity) for the "User" only.
        The "Assistant" speaker is an AI and should not be evaluated; their dialogue is 
        for context only.
        Include a justification for each score.
        Also provide an overall summary of the "User's" performance.
        Format the output as a JSON object matching the ScoringResult schema.
        Do not include markdown, explanation, or code formatting.
        """
        return prompt

    def score_conversation(self) -> ScoringResult:
        user_prompt = self._build_prompt()

        response = call_structured_llm(
            request_prompt=user_prompt,
            system_prompt=(
                'You are an expert communication coach who grades conversations based on a rubric.'
            ),
            model='gpt-4o-2024-08-06',
            output_model=ScoringResult,
        )

        return response


# Example of how to use the service
if __name__ == '__main__':
    scoring_service = ScoringService()
    scoring_result = scoring_service.score_conversation()
    print(json.dumps(scoring_result.model_dump(), indent=2))
