import json
import os
from functools import lru_cache

from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.openai_client import call_structured_llm
from app.models.language import LanguageCode
from app.schemas.session_feedback import (
    FeedbackRequest,
    GoalsAchievedCollection,
    GoalsAchievementRequest,
    RecommendationsCollection,
    SessionExamplesCollection,
)
from app.schemas.session_feedback_config import SessionFeedbackConfig
from app.services.session_feedback.session_feedback_prompt_templates import (
    build_goals_achieved_prompt,
    build_recommendations_prompt,
    build_training_examples_prompt,
)
from app.services.utils import normalize_quotes


@lru_cache
def load_session_feedback_config() -> SessionFeedbackConfig:
    config_path = os.path.join(os.path.dirname(__file__), 'session_feedback_config.json')
    with open(config_path, encoding='utf-8') as f:
        data = json.load(f)  # Python dict
    return SessionFeedbackConfig.model_validate(data)


CONFIG_PATH = os.path.join('app', 'config', 'session_feedback_config.json')
config = load_session_feedback_config()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_training_examples(
    request: FeedbackRequest, hr_docs_context: str = ''
) -> SessionExamplesCollection:
    return generate_training_examples(request, hr_docs_context)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_get_achieved_goals(
    request: GoalsAchievementRequest, hr_docs_context: str = ''
) -> GoalsAchievedCollection:
    return get_achieved_goals(request, hr_docs_context)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_recommendations(
    request: FeedbackRequest, hr_docs_context: str = ''
) -> RecommendationsCollection:
    return generate_recommendations(request, hr_docs_context)


def generate_training_examples(
    request: FeedbackRequest, hr_docs_context: str = ''
) -> SessionExamplesCollection:
    if not request.transcript or not any(
        line.strip().startswith('User:') for line in request.transcript.splitlines()
    ):
        return SessionExamplesCollection(positive_examples=[], negative_examples=[])

    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.session_examples
    system_prompt = settings.system_prompts.session_examples

    user_prompt = build_training_examples_prompt(
        category=request.category,
        transcript=request.transcript,
        objectives=request.objectives,
        persona=request.persona,
        situational_facts=request.situational_facts,
        key_concepts=request.key_concepts,
        hr_docs_context=hr_docs_context,
    )

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        model='gpt-4o-2024-08-06',
        output_model=SessionExamplesCollection,
        mock_response=mock_response,
    )

    # Normalize all quote fields to ensure consistent output
    for ex in response.positive_examples:
        ex.quote = normalize_quotes(ex.quote)
    for ex in response.negative_examples:
        ex.quote = normalize_quotes(ex.quote)
        if hasattr(ex, 'improved_quote') and ex.improved_quote:
            ex.improved_quote = normalize_quotes(ex.improved_quote)

    return response


def get_achieved_goals(
    request: GoalsAchievementRequest, hr_docs_context: str = ''
) -> GoalsAchievedCollection:
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.goals_achieved
    system_prompt = settings.system_prompts.goals_achieved

    if not request.transcript or not any(
        line.strip().startswith('User:') for line in request.transcript.splitlines()
    ):
        return GoalsAchievedCollection(goals_achieved=[])

    user_prompt = build_goals_achieved_prompt(
        transcript=request.transcript,
        objectives=request.objectives,
        hr_docs_context=hr_docs_context,
    )

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        model='gpt-4o-2024-08-06',
        output_model=GoalsAchievedCollection,
        mock_response=mock_response,
    )

    return response


def generate_recommendations(
    request: FeedbackRequest, hr_docs_context: str = ''
) -> RecommendationsCollection:
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.recommendations
    system_prompt = settings.system_prompts.recommendations

    user_prompt = build_recommendations_prompt(
        transcript=request.transcript,
        persona=request.persona,
        objectives=request.objectives,
        key_concepts=request.key_concepts,
        situational_facts=request.situational_facts,
        category=request.category,
        hr_docs_context=hr_docs_context,
    )

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        model='gpt-4o-2024-08-06',
        output_model=RecommendationsCollection,
        mock_response=mock_response,
    )

    return response


if __name__ == '__main__':
    # Example usage of the service functions
    example_request = FeedbackRequest(
        category='Termination',
        persona=(
            '**Name**: Julian '
            '**Training Focus**: Successfully conduct a termination meeting '
            '**Company Position**: Team member'
        ),
        situational_facts='Termination meeting with a team member on poor performance',
        transcript='User:  Hi, I have to talk to you. \n'
        + "Assistant: Yes, what is it? Please don't fire me, I really need this job. "
        + "I know I haven't been performing well lately, but I promise I can improve."
        + "I'll do whatever it takes."
        + 'Response interrupted'
        + "User:  I'm sorry but I'm not happy with your performance. \n"
        + 'Assistant: I understand, and I take full responsibility. \n'
        + 'Could you please tell me specifically what areas I need to improve on?'
        + "I'm willing to work late, come in early, take on extra tasks—anything "
        + 'to meet your expectations. Just please give me a chance to prove myself. \n'
        + "User:  You can't do anything it's too late to improve. \n"
        + "Assistant: Please, don't say that. I'm a hard worker, "
        "and I'm a quick learner."
        + "If you give me another chance, I promise I won't let you down."
        + 'Is there anything, anything at all, I can do to change your mind? \n',
        objectives=[
            'Bring clarity to the situation',
            'Encourage open dialogue',
            'Maintain professionalism',
            'Provide specific feedback',
            'Foster mutual understanding',
            'End on a positive note',
        ],
        key_concepts='### Active Listening\nShow empathy and paraphrase concerns.',
        language_code=LanguageCode.de,
    )

    examples = generate_training_examples(example_request)

    if len(examples.positive_examples) == 0:
        print('No positive examples found. Please check the transcript and guidelines.')
    if len(examples.negative_examples) == 0:
        print('No negative examples found. Please check the transcript and guidelines.')

    for example in examples.positive_examples:
        print(f'Positive Example: {example.heading}')
        print(f'Feedback: {example.feedback}')
        print(f'Quote: {example.quote}')

    for example in examples.negative_examples:
        print(f'Negative Example: {example.heading}')
        print(f'Feedback: {example.feedback}')
        print(f'Quote: {example.quote}')
        print(f'Improved Quote: {example.improved_quote}\n')

    print('Training examples generated successfully.')

    goals_achievement_request = GoalsAchievementRequest(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        language_code=example_request.language_code,
    )
    goals_achieved = get_achieved_goals(goals_achievement_request)
    print(
        'Number of goals achieved: '
        + f'{len(goals_achieved.goals_achieved)} / {len(example_request.objectives)}'
    )

    recommendation_request = FeedbackRequest(
        category=example_request.category,
        persona=example_request.persona,
        situational_facts=example_request.situational_facts,
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        key_concepts=example_request.key_concepts,
        language_code=example_request.language_code,
    )
    recommendations = generate_recommendations(recommendation_request)
    for recommendation in recommendations.recommendations:
        print(f'Recommendation: {recommendation.heading}')
        print(f'Recommendation: {recommendation.recommendation}\n')
    print('Recommendations generated successfully.')
