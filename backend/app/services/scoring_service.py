# ruff: noqa: E501
import json
from pathlib import Path
from typing import Any, Optional

from app.connections.openai_client import call_structured_llm
from app.schemas.conversation_scenario import ConversationScenarioWithTranscript
from app.schemas.scoring_schema import ScoringResult


class ScoringService:
    def __init__(self, rubric_path: Optional[Path] = None) -> None:
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent / 'data' / 'conversation_rubric.json'
        self.rubric = self._load_json(rubric_path)

    def _load_json(self, path: Path) -> dict[str, Any]:
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def _build_system_prompt(self) -> str:
        system_prompt = (
            'You are an expert communication coach who grades conversations based on a rubric.\n\n'
            '**Scoring Instructions:**\n'
            '- Only evaluate the User, strictly following the rubric. Ignore all Assistant content.\n'
            "- For each metric, carefully compare User's behavior to all rubric levels and select the best match.\n"
            '- If performance fully matches the lowest level, assign the lowest score. If between levels, pick the closest and explain.\n'
            '- In doubt, refer to the rubric and use your best judgment. Do not always default to the lowest.\n'
            '- Justifications must reference rubric descriptions. Be strict, fair, and consider context.\n'
            'Here is the evaluation rubric:\n'
            f'{json.dumps(self.rubric, indent=2)}'
        )
        return system_prompt

    def _build_user_prompt(self, conversation: ConversationScenarioWithTranscript) -> str:
        scenario = conversation.scenario
        transcript = conversation.transcript
        prompt = (
            '**Conversation Scenario:**\n'
            f'{getattr(scenario, "description", getattr(scenario, "context", ""))}\n'
            f'User Role: {getattr(scenario, "user_role", "User")}\n'
            f'Assistant Role: {getattr(scenario, "assistant_role", "Assistant")}\n\n'
            '**Conversation Transcript:**\n'
        )
        for turn in transcript:
            prompt += f'{turn.speaker}: {turn.text}\n'
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

    def score_conversation(
        self,
        conversation: ConversationScenarioWithTranscript,
        model: str = 'o4-mini-2025-04-16',
        temperature: float = 0.0,
    ) -> ScoringResult:
        if conversation is None:
            raise ValueError('Conversation is required')
        user_prompt = self._build_user_prompt(conversation)
        system_prompt = self._build_system_prompt()

        response = call_structured_llm(
            request_prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
            output_model=ScoringResult,
            temperature=temperature,
        )

        # Recalculate the overall score based on the rubric
        scores = {s.metric.lower(): s.score for s in response.scoring.scores}
        overall = (
            scores.get('structure', 0)
            + scores.get('empathy', 0)
            + scores.get('focus', 0)
            + scores.get('clarity', 0)
        ) / 4
        response.scoring.overall_score = overall

        return response

    def rubric_to_markdown(self) -> str:
        """
        Convert the rubric content to a human-readable Markdown format (English only).
        """
        rubric = self.rubric
        md = f'# {rubric.get("title", "")}\n\n{rubric.get("description", "")}\n\n'
        for criterion in rubric.get('criteria', []):
            md += f'## {criterion.get("name", "")}\n'
            md += f'**Criterion**: {criterion.get("description", "")}\n\n'
            levels = criterion.get('levels', {})
            for score in sorted(levels.keys(), key=lambda x: int(x), reverse=True):
                desc = levels[score]
                md += f'- **Score {score}**: {desc}\n'
            md += '\n'
        common_levels = rubric.get('common_levels', {})
        if common_levels:
            md += '## Common Levels\n'
            for score, desc in common_levels.items():
                md += f'- **Score {score}**: {desc}\n'
        return md


scoring_service = ScoringService()


def get_scoring_service() -> ScoringService:
    return scoring_service
