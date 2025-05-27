from unittest.mock import MagicMock, patch

from backend.schemas.training_feedback_schema import (
    ExamplesRequest,
    GoalAchieved,
    GoalAchievementRequest,
    Recommendation,
    RecommendationsCollection,
    RecommendationsRequest,
    TrainingExamplesCollection,
)
from backend.services.training_feedback_service import (
    generate_recommendations,
    generate_training_examples,
    get_achieved_goals,
)


@patch('backend.services.training_feedback_service.call_structured_llm')
def test_generate_training_examples(mock_client: MagicMock) -> None:
    mock_client.return_value = TrainingExamplesCollection(
        positive_examples="""**Maintaining Professionalism**  
        - **Explanation:** The attempt to address the performance issue directly, 
        without hostility, maintains a professional tone.
        - **Quote:** "I'm sorry but I'm not happy with your performance."
        - **Relevant Guideline:** Maintain professionalism.
                           """,
        negative_examples="""**Lack of Specific Feedback**  
        - **Explanation:** Failing to provide specific areas of improvement does not give the 
        team member clarity on their shortcomings.
        - **Quote:** "I'm sorry but I'm not happy with your performance."
        - **Suggested Improvement:** Provide specific examples of performance issues to help the 
        team member understand and accept the decision.

        **Closing Off Open Dialogue**  
        - **Explanation:** Abruptly stating that nothing can change fails to encourage an 
        open dialogue and does not foster understanding.
        - **Quote:** "You can't do anything it's too late to improve."
        - **Suggested Improvement:** Allow the team member to express their concerns and 
        acknowledge their willingness to improve.

        **Ending on a Positive Note**  
        - **Explanation:** The conversation ends on a negative note without acknowledging the 
        team member's contributions or potential future opportunities.
        - **Quote:** "You can't do anything it's too late to improve."
        - **Suggested Improvement:** Conclude with positive remarks about the person's skills 
        or contributions and suggest ways they can grow in the future.""",
    )

    request = ExamplesRequest(
        category='Feedback',
        goal='Deliver constructive feedback',
        context='Performance review',
        other_party='Team member',
        transcript='User: I want to make sure we both feel heard..., '
        + 'AI: ..., '
        + "User: That's not important right now...",
        objectives=['Foster mutual understanding', 'Encourage open dialogue'],
        key_concepts='### Active Listening\nShow empathy and paraphrase concerns.',
    )

    result = generate_training_examples(request)
    assert isinstance(result, TrainingExamplesCollection)


@patch('backend.services.training_feedback_service.call_structured_llm')
def test_get_achieved_goals(mock_client: MagicMock) -> None:
    mock_client.return_value = GoalAchieved(goals_achieved=2)

    transcript = "User: I understand your frustration. Let's find a solution together."
    goals = [
        'Clearly communicate the impact of the missed deadlines',
        'Understand potential underlying causes',
        'Collaboratively develop a solution',
        'End the conversation on a positive note',
    ]

    request = GoalAchievementRequest(
        transcript=transcript,
        objectives=goals,
    )
    result = get_achieved_goals(request)
    assert result == 2


@patch('backend.services.training_feedback_service.call_structured_llm')
def test_generate_recommendations(mock_client: MagicMock) -> None:
    transcript = "User: Let's explore what might be causing these delays."
    objectives = ['Understand root causes', 'Collaboratively develop a solution']
    goal = 'Improve team communication'
    key_concepts = '### Active Listening\nAsk open-ended questions.'
    context = 'Project delay review'
    category = 'Project Management'
    other_party = 'Colleague'

    mock_client.return_value = RecommendationsCollection(
        recommendations=[
            Recommendation(
                markdown='#### Practice the STAR method\n'
                'Use the STAR method to structure your feedback: Situation, Task, Action, Result. '
            ),
            Recommendation(
                markdown='#### Focus on specific behaviors\n'
                'Identify specific behaviors rather than generalizations.'
            ),
            Recommendation(
                markdown='#### Encourage open dialogue\n'
                'Foster an environment where both parties can share their perspectives.'
            ),
        ]
    )

    request = RecommendationsRequest(
        category=category,
        context=context,
        other_party=other_party,
        transcript=transcript,
        objectives=objectives,
        goal=goal,
        key_concepts=key_concepts,
    )
    result = generate_recommendations(request)
    assert len(result.recommendations) == 3
    assert (
        result.recommendations[0].markdown == '#### Practice the STAR method\n'
        'Use the STAR method to structure your feedback: Situation, Task, Action, Result. '
    )
