"""Service layer for scoring service."""

# ruff: noqa: E501
import json
from pathlib import Path
from typing import Any

from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.vertexai_client import call_structured_llm
from app.schemas.conversation_scenario import ConversationScenarioRead
from app.schemas.scoring_schema import ScoringRead
from app.services.utils import normalize_quotes


class ScoringService:
    """Service for scoring conversations with an LLM rubric."""

    def __init__(self, rubric_path: Path | None = None) -> None:
        """Initialize the scoring service with a rubric file.

        Parameters:
            rubric_path (Path | None): Optional path to the rubric JSON file.
        """
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent / 'data' / 'conversation_rubric.json'
        self.rubric = self._load_json(rubric_path)

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load a JSON file from disk.

        Parameters:
            path (Path): Path to the JSON file.

        Returns:
            dict[str, Any]: Parsed JSON content.
        """
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def _build_system_prompt(self) -> str:
        """Build the system prompt for conversation scoring.

        Returns:
            str: System prompt content.
        """
        system_prompt = (
            'You are an expert communication coach who grades conversations based on the following rubric.\n\n'
            '**Scoring Instructions:**\n'
            "- For every metric, ONLY consider the User's utterances. Ignore all Assistant utterances.\n"
            "- For each metric, select the score (1-5) that best matches the User's overall performance.\n"
            '- In your justification, briefly explain why you chose this score, focusing on the main strengths and weaknesses.\n'
            '- Do NOT be overly strict: perfection is not required for a 5. If the User generally demonstrates the qualities of a 5, give a 5.\n'
            "- If the User's utterances are completely irrelevant or incomprehensible, assign a score of 1 for that metric.\n"
            '- Output must be a valid JSON object matching the ScoringRead schema. Do not include markdown, explanations, or code formatting.\n'
            'Here is the evaluation rubric:\n'
            f'{json.dumps(self.rubric, indent=2)}'
            '\n\n'
            "You MUST act as if the Assistant's utterances do not exist at all. Only the User's utterances are relevant for scoring. If you mention or consider the Assistant in your justification, that is a mistake.\n"
            "Please also take into account the user's vocal emotion, tone, and expressive style in your evaluation if audio is provided."
        )
        return system_prompt

    def _build_user_prompt(self, conversation: ConversationScenarioRead) -> str:
        """Build the user prompt from a conversation transcript.

        Parameters:
            conversation (ConversationScenarioRead): Scenario and transcript payload.

        Returns:
            str: User prompt content.
        """
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
            '(structure, empathy, focus, clarity) for the "User" only, and give a brief justification for each score.\n'
            "If the User's performance mostly meets the criteria for a high score, even with minor lapses, you should give a high score.\n"
            'Format the output as a JSON object matching the ScoringRead schema. Do not include markdown, explanation, or code formatting.\n'
        )
        return prompt

    def score_conversation(
        self,
        conversation: ConversationScenarioRead,
        temperature: float = 0.0,
        audio_uri: str | None = None,
    ) -> ScoringRead:
        """Score a conversation and return structured results.

        Parameters:
            conversation (ConversationScenarioRead): Scenario and transcript payload.
            temperature (float): Sampling temperature for the LLM.
            audio_uri (str | None): Optional audio URI for additional cues.

        Returns:
            ScoringRead: Structured scoring output.
        """
        user_prompt = self._build_user_prompt(conversation)
        system_prompt = self._build_system_prompt()

        response = call_structured_llm(
            request_prompt=user_prompt,
            system_prompt=system_prompt,
            output_model=ScoringRead,
            temperature=temperature,
            audio_uri=audio_uri,
        )

        # Recalculate the overall score based on the rubric
        response.scoring.scores = [
            s.model_copy(update={'metric': s.metric.lower()}) for s in response.scoring.scores
        ]
        scores = {s.metric: s.score for s in response.scoring.scores}
        response.scoring.overall_score = sum(scores.values())

        # Normalize all quotes in the response
        response.conversation_summary = normalize_quotes(response.conversation_summary)
        for score in response.scoring.scores:
            score.justification = normalize_quotes(score.justification)

        return response

    def rubric_to_markdown(self) -> str:
        """Convert the rubric content to a human-readable Markdown format (English only).

        Returns:
            str: Human-readable Markdown representation of the rubric.
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
    def safe_score_conversation(self, conversation: ConversationScenarioRead) -> ScoringRead:
        """Retry scoring for transient failures.

        Parameters:
            conversation (ConversationScenarioRead): Scenario and transcript payload.

        Returns:
            ScoringRead: Structured scoring output.
        """
        return self.score_conversation(conversation)


scoring_service = ScoringService()


def get_scoring_service() -> ScoringService:
    """Return the singleton scoring service instance.

    Returns:
        ScoringService: Shared scoring service.
    """
    return scoring_service
