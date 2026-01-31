"""Service layer for session feedback llm."""

import json
import os
from functools import lru_cache

from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.vertexai_client import call_structured_llm
from app.enums.language import LANGUAGE_NAME, LanguageCode
from app.schemas.session_feedback import (
    FeedbackCreate,
    GoalsAchievedCreate,
    GoalsAchievedRead,
    RecommendationsRead,
    SessionExamplesRead,
)
from app.schemas.session_feedback_config import SessionFeedbackConfigRead
from app.services.session_feedback.session_feedback_prompt_templates import (
    build_goals_achieved_prompt,
    build_recommendations_prompt,
    build_training_examples_prompt,
)
from app.services.utils import normalize_quotes


@lru_cache
def load_session_feedback_config() -> SessionFeedbackConfigRead:
    """Load session feedback configuration from disk.

    Returns:
        SessionFeedbackConfigRead: Parsed configuration model.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'session_feedback_config.json')
    with open(config_path, encoding='utf-8') as f:
        data = json.load(f)  # Python dict
    return SessionFeedbackConfigRead.model_validate(data)


CONFIG_PATH = os.path.join('app', 'config', 'session_feedback_config.json')
config = load_session_feedback_config()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_training_examples(
    request: FeedbackCreate,
    hr_docs_context: str = '',
    audio_uri: str | None = None,
    temperature: float = 0.0,
) -> SessionExamplesRead:
    """Retry-safe wrapper to generate training examples.

    Parameters:
        request (FeedbackCreate): Feedback request payload.
        hr_docs_context (str): HR document context.
        audio_uri (str | None): Optional audio URI.
        temperature (float): Sampling temperature.

    Returns:
        SessionExamplesRead: Generated example pairs.
    """
    return generate_training_examples(request, hr_docs_context, audio_uri, temperature)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_get_achieved_goals(
    request: GoalsAchievedCreate,
    hr_docs_context: str = '',
    audio_uri: str | None = None,
    temperature: float = 0.0,
) -> GoalsAchievedRead:
    """Retry-safe wrapper to get achieved goals.

    Parameters:
        request (GoalsAchievedCreate): Goals request payload.
        hr_docs_context (str): HR document context.
        audio_uri (str | None): Optional audio URI.
        temperature (float): Sampling temperature.

    Returns:
        GoalsAchievedRead: Achieved goals response.
    """
    if audio_uri is not None:
        return get_achieved_goals(request, hr_docs_context, audio_uri, temperature=temperature)
    else:
        return get_achieved_goals(request, hr_docs_context, temperature=temperature)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_recommendations(
    request: FeedbackCreate,
    hr_docs_context: str = '',
    audio_uri: str | None = None,
    temperature: float = 0.0,
) -> RecommendationsRead:
    """Retry-safe wrapper to generate recommendations.

    Parameters:
        request (FeedbackCreate): Feedback request payload.
        hr_docs_context (str): HR document context.
        audio_uri (str | None): Optional audio URI.
        temperature (float): Sampling temperature.

    Returns:
        RecommendationsRead: Recommendations response.
    """
    return generate_recommendations(request, hr_docs_context, audio_uri, temperature)


def generate_training_examples(
    request: FeedbackCreate,
    hr_docs_context: str = '',
    audio_uri: str | None = None,
    temperature: float = 0.0,
) -> SessionExamplesRead:
    """Generate positive and negative training examples.

    Parameters:
        request (FeedbackCreate): Feedback request payload.
        hr_docs_context (str): HR document context.
        audio_uri (str | None): Optional audio URI.
        temperature (float): Sampling temperature.

    Returns:
        SessionExamplesRead: Generated training examples.
    """
    if not request.transcript or all(
        (line.strip() == '' or line.strip().startswith('Assistant:'))
        for line in request.transcript.splitlines()
    ):
        return SessionExamplesRead(positive_examples=[], negative_examples=[])
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.session_examples
    system_prompt = settings.system_prompts.session_examples

    lang_name = LANGUAGE_NAME.get(lang, 'English')
    user_prompt = build_training_examples_prompt(
        category=request.category,
        transcript=request.transcript,
        objectives=request.objectives,
        persona=request.persona,
        situational_facts=request.situational_facts,
        key_concepts=request.key_concepts,
        hr_docs_context=hr_docs_context,
        language_name=lang_name,
    )

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        output_model=SessionExamplesRead,
        temperature=temperature,
        mock_response=mock_response,
        audio_uri=audio_uri,
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
    request: GoalsAchievedCreate,
    hr_docs_context: str = '',
    audio_uri: str | None = None,
    temperature: float = 0.0,
) -> GoalsAchievedRead:
    """Evaluate achieved goals from a transcript.

    Parameters:
        request (GoalsAchievedCreate): Goals request payload.
        hr_docs_context (str): HR document context.
        audio_uri (str | None): Optional audio URI.
        temperature (float): Sampling temperature.

    Returns:
        GoalsAchievedRead: Achieved goals response.
    """
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.goals_achieved
    system_prompt = settings.system_prompts.goals_achieved

    lang_name = LANGUAGE_NAME.get(lang, 'English')
    user_prompt = build_goals_achieved_prompt(
        transcript=request.transcript,
        objectives=request.objectives,
        hr_docs_context=hr_docs_context,
        language_name=lang_name,
    )

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        output_model=GoalsAchievedRead,
        temperature=temperature,
        mock_response=mock_response,
        audio_uri=audio_uri,
    )

    response.goals_achieved = [goal for goal in response.goals_achieved if goal.strip()]
    return response


def generate_recommendations(
    request: FeedbackCreate,
    hr_docs_context: str = '',
    audio_uri: str | None = None,
    temperature: float = 0.0,
) -> RecommendationsRead:
    """Generate coaching recommendations from a transcript.

    Parameters:
        request (FeedbackCreate): Feedback request payload.
        hr_docs_context (str): HR document context.
        audio_uri (str | None): Optional audio URI.
        temperature (float): Sampling temperature.

    Returns:
        RecommendationsRead: Recommendations response.
    """
    if not request.transcript or all(
        (line.strip() == '' or line.strip().startswith('Assistant:'))
        for line in request.transcript.splitlines()
    ):
        return RecommendationsRead(recommendations=[])
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.recommendations
    system_prompt = settings.system_prompts.recommendations

    lang_name = LANGUAGE_NAME.get(lang, 'English')
    user_prompt = build_recommendations_prompt(
        transcript=request.transcript,
        persona=request.persona,
        objectives=request.objectives,
        key_concepts=request.key_concepts,
        situational_facts=request.situational_facts,
        category=request.category,
        hr_docs_context=hr_docs_context,
        language_name=lang_name,
    )

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        output_model=RecommendationsRead,
        temperature=temperature,
        mock_response=mock_response,
        audio_uri=audio_uri,
    )

    return response


if __name__ == '__main__':
    # Example usage of the service functions
    example_request = FeedbackCreate(
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

    goals_achievement_request = GoalsAchievedCreate(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        language_code=example_request.language_code,
    )
    goals_achieved = get_achieved_goals(goals_achievement_request)
    print(
        'Number of goals achieved: '
        + f'{len(goals_achieved.goals_achieved)} / {len(example_request.objectives)}'
    )

    recommendation_request = FeedbackCreate(
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
