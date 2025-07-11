# ruff: noqa: E501
import json
from pathlib import Path
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.openai_client import call_structured_llm
from app.schemas.conversation_scenario import ConversationScenarioWithTranscript
from app.schemas.scoring_schema import ScoringResult
from app.services.utils import normalize_quotes


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
            'You are an expert communication coach who grades conversations based on a strict rubric.\n\n'
            '**Scoring Instructions:**\n'
            "- For every metric, you MUST ONLY consider the User's utterances. Completely ignore all Assistant utterances, even if they are helpful, on-topic, or try to bring the conversation back to focus.\n"
            "- For each metric, in your justification, explicitly compare the User's behavior to every rubric level (1-5), and state why it does or does not meet each level. Only after this comparison, select the best matching score.\n"
            '- You MUST provide a score and justification for ALL FOUR metrics: structure, empathy, focus, and clarity. Do not omit any metric, even if the performance is very poor.\n'
            "- If the User's utterances are completely irrelevant, incomprehensible, or show no attempt to engage with the metric, you MUST assign a score of 1 for that metric.\n"
            '- If the overall performance is good enough and only contains minor lapses or imperfections, a score of 5 is appropriate.\n'
            'Here is the evaluation rubric:\n'
            "- You may use the common levels (e.g., 0) as a reference for scoring if the user's utterances are completely irrelevant, incomprehensible, or show no attempt to engage with the metric.\n"
            f'{json.dumps(self.rubric, indent=2)}'
            '\n\n'
            "You MUST act as if the Assistant's utterances do not exist at all. Only the User's utterances are relevant for scoring. If you mention or consider the Assistant in your justification, that is a mistake.\n"
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
        response.scoring.scores = [
            s.model_copy(update={'metric': s.metric.lower()}) for s in response.scoring.scores
        ]
        scores = {s.metric: s.score for s in response.scoring.scores}
        overall = (
            scores['structure'] + scores['empathy'] + scores['focus'] + scores['clarity']
        ) / 4
        response.scoring.overall_score = overall

        # Normalize all quotes in the response
        response.conversation_summary = normalize_quotes(response.conversation_summary)
        for score in response.scoring.scores:
            score.justification = normalize_quotes(score.justification)

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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def safe_score_conversation(
        self, conversation: ConversationScenarioWithTranscript
    ) -> ScoringResult:
        return self.score_conversation(conversation)


scoring_service = ScoringService()


def get_scoring_service() -> ScoringService:
    return scoring_service
