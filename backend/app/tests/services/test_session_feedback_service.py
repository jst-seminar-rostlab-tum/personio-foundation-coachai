from unittest.mock import MagicMock, patch

from app.schemas.session_feedback_schema import (
    ExamplesRequest,
    GoalsAchievedCollection,
    GoalsAchievementRequest,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsCollection,
    RecommendationsRequest,
    SessionExamplesCollection,
)
from app.services.session_feedback_service import (
    generate_recommendations,
    generate_training_examples,
    get_achieved_goals,
)


@patch('app.services.session_feedback_service.call_structured_llm')
def test_generate_training_examples(mock_client: MagicMock) -> None:
    mock_client.return_value = SessionExamplesCollection(
        positive_examples=[
            PositiveExample(
                heading='Clear Objective Addressed',
                text='The user successfully summarized the objective.',
                quote='I want to make sure we both feel heard and find a solution together.',
                guideline='Collaborative Problem-Solving',
            )
        ],
        negative_examples=[
            NegativeExample(
                heading='Missed Empathy',
                text="The user dismissed the other party's concern.",
                quote="That's not important right now.",
                improved_quote="I understand your concern—let's come back to it in a moment.",
            )
        ],
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
    assert isinstance(result, SessionExamplesCollection)
    assert len(result.positive_examples) == 1
    assert len(result.negative_examples) == 1
    assert result.positive_examples[0].heading == 'Clear Objective Addressed'
    assert result.negative_examples[0].quote == "That's not important right now."


@patch('app.services.session_feedback_service.call_structured_llm')
def test_get_achieved_goals(mock_client: MagicMock) -> None:
    mock_client.return_value = GoalsAchievedCollection(
        goals_achieved=[
            'Clearly communicate the impact of the missed deadlines',
            'Understand potential underlying causes',
        ]
    )

    transcript = "User: I understand your frustration. Let's find a solution together."
    goals = [
        'Clearly communicate the impact of the missed deadlines',
        'Understand potential underlying causes',
        'Collaboratively develop a solution',
        'End the conversation on a positive note',
    ]

    request = GoalsAchievementRequest(
        transcript=transcript,
        objectives=goals,
    )
    result = get_achieved_goals(request)
    assert isinstance(result, GoalsAchievedCollection)


@patch('app.services.session_feedback_service.call_structured_llm')
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
                heading='Practice the STAR method',
                text='When giving feedback, use the Situation, Task, Action, Result framework to '
                + 'provide more concrete examples.',
            ),
            Recommendation(
                heading='Ask more diagnostic questions',
                text='Spend more time understanding root causes before moving to solutions. '
                + 'This builds empathy and leads to more effective outcomes.',
            ),
            Recommendation(
                heading='Define clear next steps',
                text='End feedback conversations with agreed-upon action items, timelines, and'
                + ' follow-up plans.',
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
    assert result.recommendations[0].heading == 'Practice the STAR method'
