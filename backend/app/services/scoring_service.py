import json
from pathlib import Path
from typing import Any

from app.schemas.scoring_schema import ScoringResult


class ScoringService:
    def __init__(self, rubric_path: Path = None, conversation_path: Path = None) -> None:
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent / 'data' / 'conversation_rubric.json'
        if conversation_path is None:
            conversation_path = (
                Path(__file__).parent.parent / 'data' / 'dummy_conversation_for_testing.json'
            )

        self.rubric = self._load_json(rubric_path)
        self.conversation_data = self._load_json(conversation_path)

    def _load_json(self, path: Path) -> dict[str, Any]:
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def _build_prompt(self) -> str:
        # This is a simplified representation of the prompt building logic.
        # In a real scenario, this would be a carefully crafted prompt template.
        prompt = f"""
        Please score the following conversation based on the provided rubric.
        
        **Rubric:**
        {json.dumps(self.rubric, indent=2)}

        **Conversation Transcript:**
        Scenario: {self.conversation_data['scenario']['description']}
        """
        for turn in self.conversation_data['transcript']:
            prompt += f'{turn["speaker"]}: {turn["message"]}\n'

        prompt += """
        Provide a score from 0-5 for each metric (Structure, Empathy, Focus, Clarity) 
        with a justification for each score.
        Also provide an overall summary.
        Format the output as a JSON object matching the ScoringResult schema.
        """
        return prompt

    def score_conversation(self) -> ScoringResult:
        # In a real implementation, you would send the prompt to an LLM.
        # Here, we are mocking the response for demonstration and testing purposes.
        # prompt = self._build_prompt()
        # llm_response = call_llm_api(prompt)
        # For now, we use a hardcoded mock response.

        mock_llm_response = {
            'conversation_summary': (
                'The manager, Alex, provided structured and empathetic feedback to Sam '
                'regarding communication issues. While Sam was initially defensive, Alex '
                'skillfully guided the conversation to a productive outcome, with clear '
                'action items agreed upon.'
            ),
            'scoring': {
                'overall_score': 4.25,
                'scores': [
                    {
                        'metric': 'Structure',
                        'score': 5,
                        'justification': (
                            'The conversation was very well-structured. Alex started with a '
                            'general question, narrowed down to the specific issue, '
                            'explained the impact, and collaboratively found a solution '
                            'before summarizing the next steps.'
                        ),
                    },
                    {
                        'metric': 'Empathy',
                        'score': 4,
                        'justification': (
                            "Alex showed good empathy by acknowledging Sam's personal "
                            "situation ('I understand that personal things come up'). It "
                            'could have been slightly higher if the initial check-in felt '
                            'more personal, but it was effective.'
                        ),
                    },
                    {
                        'metric': 'Focus',
                        'score': 4,
                        'justification': (
                            'The conversation remained highly focused on the communication '
                            "issue. Sam's brief mention of being 'swamped' was a slight "
                            'deviation, but Alex skillfully brought the focus back to the '
                            'impact on the team.'
                        ),
                    },
                    {
                        'metric': 'Clarity',
                        'score': 4,
                        'justification': (
                            "Alex's communication was clear and direct, using specific "
                            "examples ('missed a couple of the recent project syncs'). "
                            "Sam's initial responses were somewhat vague ('it's fine'), "
                            'but the final agreement was clear.'
                        ),
                    },
                ],
            },
        }

        return ScoringResult(**mock_llm_response)


# Example of how to use the service
if __name__ == '__main__':
    scoring_service = ScoringService()
    scoring_result = scoring_service.score_conversation()
    print(json.dumps(scoring_result.dict(), indent=2))
    # print("\n--- Generated Prompt ---")
    # print(scoring_service._build_prompt())
