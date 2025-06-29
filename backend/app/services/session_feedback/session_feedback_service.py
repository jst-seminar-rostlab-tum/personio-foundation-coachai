import concurrent.futures
import json
import os
from datetime import datetime
from functools import lru_cache
from uuid import UUID, uuid4

from sqlmodel import Session as DBSession
from sqlmodel import select
from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.openai_client import call_structured_llm
from app.models import FeedbackStatusEnum, SessionFeedback, UserProfile
from app.models.language import LanguageCode
from app.schemas.session_feedback import (
    ExamplesRequest,
    GoalsAchievedCollection,
    GoalsAchievementRequest,
    RecommendationsCollection,
    RecommendationsRequest,
    SessionExamplesCollection,
)
from app.schemas.session_feedback_config import SessionFeedbackConfig
from app.services.vector_db_context_service import query_vector_db_and_prompt


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
    request: ExamplesRequest, hr_docs_context: str = ''
) -> SessionExamplesCollection:
    return generate_training_examples(request, hr_docs_context)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_get_achieved_goals(
    request: GoalsAchievementRequest, hr_docs_context: str = ''
) -> GoalsAchievedCollection:
    return get_achieved_goals(request, hr_docs_context)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_recommendations(
    request: RecommendationsRequest, hr_docs_context: str = ''
) -> RecommendationsCollection:
    return generate_recommendations(request, hr_docs_context)


def generate_training_examples(
    request: ExamplesRequest, hr_docs_context: str = ''
) -> SessionExamplesCollection:
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.session_examples
    system_prompt = settings.system_prompts.session_examples

    user_prompt = f"""
    The following is a training session transcript in which you are practicing 
    communication skills in the context of {request.category}. 
    You are expected to follow the training guidelines provided below.
    The AI simulates the other party in the conversation, and you are expected to respond
    appropriately based on the training objectives, goal, context, and key concepts.
    In this session, you are practicing how to {request.goal} in the context of {request.context}.
    The other party, the AI, is simulating a {request.other_party}.

    **Speaker labels in the transcript:**
    - Lines starting with **"User:"** are your own statements.
    - Lines starting with **"Assistant:"** are the AI's responses and are for context only.

    Transcript:
    {request.transcript}

    Training Guidelines:
    - Objectives: {request.objectives}
    - Goal: {request.goal}
    - Context: {request.context}
    - Key Concepts: {request.key_concepts}
    
    HR Document Context:
    {hr_docs_context}

    Instructions:
    Carefully analyze the provided transcript and evaluate **only your own statements** 
    (what you said as the User).  
    **Do not analyze, quote, or critique any statements made by the Assistant.**  
    The Assistant’s lines are for context only.

    Extract up to 3 positive and up to 3 negative examples of your own communication, comparing 
    them to the training guidelines. 
    Always find at least one positive and one negative example, if possible.

    Format your output as a Pydantic model with two fields:
    - `positive_examples`: a list of up to 3 positive examples
    - `negative_examples`: a list of up to 3 negative examples

    Each positive example must include:
    - **heading**: A short summary title
    - **feedback:** A bullet point explaining why this is good practice
    - **quote:** A bullet point with the exact quote from your own lines in the transcript

    Each negative example must include:
    - **heading**: A short summary title
    - **feedback:** A bullet point explaining what could be improved
    - **quote:** A bullet point with the exact quote from your own lines in the transcript
    - **improved_quote:** A bullet point with a clear, improved version of that quote

    Do not include markdown code blocks, JSON, or extra commentary—just provide the two markdown 
    strings as the values for the Pydantic fields.
    """

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        model='gpt-4o-2024-08-06',
        output_model=SessionExamplesCollection,
        mock_response=mock_response,
    )

    return response


def get_achieved_goals(
    request: GoalsAchievementRequest, hr_docs_context: str = ''
) -> GoalsAchievedCollection:
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.goals_achieved
    system_prompt = settings.system_prompts.goals_achieved

    user_prompt = f"""
    The following is a transcript of a training session.
    Please evaluate which of the listed goals were clearly achieved by the user 
    in this conversation.

    Transcript:
    {request.transcript}

    Goals:
    {request.objectives}
    
    HR Document Context:
    {hr_docs_context}

    Instructions:
    - For each goal, determine if the user's speech aligns with 
        and fulfills the intention behind it.
    - Only count goals that are clearly demonstrated in the user's statements.

    - Format your output as a list of strings, where each string is a goal that was achieved.
    - Do not include any additional commentary or formatting.
    - Only return the list of achieved goals, not the entire transcript or any other text.
    - If no goals were achieved, return an empty list.
    - If some goals were achieved, return a list of those goals.
    - If all goals were achieved, return the full list of goals.
    - Do not include any markdown formatting or extra text.
    """

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        model='gpt-4o-2024-08-06',
        output_model=GoalsAchievedCollection,
        mock_response=mock_response,
    )

    return response


def generate_recommendations(
    request: RecommendationsRequest, hr_docs_context: str = ''
) -> RecommendationsCollection:
    lang = request.language_code
    settings = config.root[lang]

    mock_response = settings.mocks.recommendations
    system_prompt = settings.system_prompts.recommendations

    user_prompt = f"""
    Analyze the following transcript from a training session.
    Based on the goal, objectives, and key concepts, suggest 3 to 5 specific, actionable 
    communication improvement recommendations for the user.

    Each recommendation should:
    - Be based directly on how the user performed in the transcript
    - Be short, specific, and actionable

    Transcript:
    {request.transcript}

    Training Goal:
    {request.goal}

    Objectives:
    {request.objectives}

    Key Concepts:
    {request.key_concepts}

    Context:
    {request.context}
    
    HR Document Context:
    {hr_docs_context}

    Situation:
    - The conversation of this training session is about {request.category}
    - You are practicing how to {request.goal}
    - The other party, the AI, is simulating a {request.other_party}

    Format your output as a list of 'Recommendation' objects.
    Each recommendation represents a Pydantic model with two fields:
    - `heading`: A short title or summary of the recommendation
    - `recommendation`: A description or elaboration of the recommendation

    Do not include markdown, explanation, or code formatting.

    Example Recommendations:
    1. heading: "Practice the STAR method", 
    recommendation: "When giving feedback, use the Situation, Task, Action, 
    Result framework to provide more concrete examples."
    
    2. heading: "Ask more diagnostic questions", 
    recommendation: "Spend more time understanding root causes before moving to solutions. 
    This builds empathy and leads to more effective outcomes."

    3. heading: "Define clear next steps",
    recommendation: "End feedback conversations with agreed-upon action items, 
    timelines, and follow-up plans."

    """
    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=system_prompt,
        model='gpt-4o-2024-08-06',
        output_model=RecommendationsCollection,
        mock_response=mock_response,
    )

    return response


def generate_and_store_feedback(
    session_id: UUID, example_request: ExamplesRequest, db_session: DBSession
) -> SessionFeedback:
    """
    Generate feedback based on session_id and transcript data,
    and write it to the session_feedback table
    """

    has_error = False

    examples_request = example_request
    goals_request = GoalsAchievementRequest(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        language_code=example_request.language_code,
    )
    recommendations_request = RecommendationsRequest(
        category=example_request.category,
        goal=example_request.goal,
        context=example_request.context,
        other_party=example_request.other_party,
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        key_concepts=example_request.key_concepts,
        language_code=example_request.language_code,
    )

    # initialize fallback values
    examples_positive_dicts = []
    examples_negative_dicts = []
    goals = GoalsAchievedCollection(goals_achieved=[])
    recommendations = []

    hr_docs_context = query_vector_db_and_prompt(
        session_context=[
            recommendations_request.category,
            recommendations_request.goal,
            recommendations_request.context,
            recommendations_request.other_party,
            recommendations_request.transcript,
            recommendations_request.objectives,
            recommendations_request.key_concepts,
        ],
        generated_object='output',
    )

    if example_request.transcript is None:
        # No transcript: leave examples empty and goals achieved as zero
        examples_positive_dicts = []
        examples_negative_dicts = []
        goals = GoalsAchievedCollection(goals_achieved=[])
        recommendations = []
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_examples = executor.submit(
                safe_generate_training_examples, examples_request, hr_docs_context
            )
            future_goals = executor.submit(safe_get_achieved_goals, goals_request, hr_docs_context)
            future_recommendations = executor.submit(
                safe_generate_recommendations, recommendations_request, hr_docs_context
            )

            try:
                examples = future_examples.result()
                examples_positive_dicts = [ex.model_dump() for ex in examples.positive_examples]
                examples_negative_dicts = [ex.model_dump() for ex in examples.negative_examples]
            except Exception as e:
                has_error = True
                print('[ERROR] Failed to generate examples:', e)

            try:
                goals = future_goals.result()
            except Exception as e:
                has_error = True
                print('[ERROR] Failed to generate goals:', e)

            try:
                recs = future_recommendations.result()
                recommendations = [rec.model_dump() for rec in recs.recommendations]
            except Exception as e:
                has_error = True
                print('[ERROR] Failed to generate key recommendations:', e)

    # correct placement
    status = FeedbackStatusEnum.failed if has_error else FeedbackStatusEnum.completed

    feedback = SessionFeedback(
        id=uuid4(),
        session_id=session_id,
        scores={},
        tone_analysis={},
        overall_score=0,
        transcript_uri='',
        speak_time_percent=0,
        questions_asked=0,
        session_length_s=0,
        goals_achieved=goals.goals_achieved,
        example_positive=examples_positive_dicts,
        example_negative=examples_negative_dicts,
        recommendations=recommendations,
        status=status,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Update user profile with feedback
    user = db_session.exec(select(UserProfile).where(UserProfile.id == session_id)).first()
    if user:
        user.goals_achieved += len(goals.goals_achieved)
        db_session.add(user)
        db_session.commit()

    db_session.add(feedback)
    db_session.commit()

    return feedback


if __name__ == '__main__':
    # Example usage of the service functions
    example_request = ExamplesRequest(
        category='Termination',
        goal='Successfully conduct a termination meeting',
        context='Termination meeting with a team member on poor performance',
        other_party='Team member',
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

    recommendation_request = RecommendationsRequest(
        category=example_request.category,
        goal=example_request.goal,
        context=example_request.context,
        other_party=example_request.other_party,
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
