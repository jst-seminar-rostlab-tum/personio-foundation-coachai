from datetime import datetime
from uuid import uuid4

from backend.connections.openai_client import call_structured_llm
from backend.schemas.training_feedback_schema import (
    ExamplesRequest,
    GoalsAchievedCollection,
    GoalsAchievementRequest,
    RecommendationsCollection,
    RecommendationsRequest,
    TrainingExamplesCollection,
)
from sqlmodel import Session

from models import TrainingSessionFeedback
from models.training_session_feedback import FeedbackStatusEnum


def generate_training_examples(request: ExamplesRequest) -> TrainingExamplesCollection:
    user_prompt = f"""
    The following is a training session transcript, in which you are practicing 
    communication skills in the context of {request.category}. 
    You are expected to follow the training guidelines provided below.
    The AI simulates the other party in the conversation, and you are expected to respond
    appropriately based on the training objectives, goal, context, and key concepts.
    In this case, you are practicing how to {request.goal} in the context of {request.context}.
    The other party, the AI, is simulating a {request.other_party}.

    Transcript:
    {request.transcript}

    Training Guidelines:
    - Objectives: {request.objectives}
    - Goal: {request.goal}
    - Context: {request.context}
    - Key Concepts: {request.key_concepts}

    Instructions:
    Analyze the provided transcript and how you performed against the training guidelines. 
    Extract up to 3 positive and 3 negative examples comparing your performance to the 
    training guidelines. Only extract examples that are things you said (not the AI).
    Try to find at least one positive and one negative example.

    Format your output as a Pydantic model with two fields:
    - `positive_examples`: a list of up to 3 positive examples
    - `negative_examples`: a list of up to 3 negative examples.

    Each positive example represents a Pydantic model with the four fields:
    - `heading`: A short title or summary of the positive example
    - `text`: A short explanation of why this is a good example
    - `quote`: A direct quote from the transcript that illustrates the example
    - `guideline`: The specific guideline or concept this quote aligns with
    
    Each negative example represents a Pydantic model with the four fields:
    - `heading`: A short title or summary of the negative example
    - `text`: A short description or context of the example
    - `quote`: A problematic or unhelpful quote mentioned by the user
    - `improved_quote`: A suggested improved version of the quote
    
    Do not include markdown or ```json formatting.

    Each example should include:
    - A bolded heading
    - A bullet point explanation under **"Explanation:"**
    - A bullet point quote under **"Quote:"**
    - For positive examples: a bullet point **"Relevant Guideline:"**
    - For negative examples: a bullet point **"Suggested Improvement:"**

    Do not include any headings, commentary, or extra formatting—just provide the two markdown 
    strings as values for the Pydantic fields.
    """

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are an expert communication coach analyzing training sessions.',
        model='gpt-4o-2024-08-06',
        output_model=TrainingExamplesCollection,
    )

    return response


def get_achieved_goals(request: GoalsAchievementRequest) -> GoalsAchievedCollection:
    user_prompt = f"""
    The following is a transcript of a training session.
    Please evaluate which of the listed goals were clearly achieved by the user 
    in this conversation.

    Transcript:
    {request.transcript}

    Goals:
    {request.objectives}

    Instructions:
    - For each goal, determine if the user’s speech aligns with 
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
        system_prompt='You are an expert communication coach analyzing training sessions.',
        model='gpt-4o-2024-08-06',
        output_model=GoalsAchievedCollection,
    )

    return response


def generate_recommendations(request: RecommendationsRequest) -> RecommendationsCollection:
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

    Situation:
    - The conversation of this training session is about {request.category}
    - You are practicing how to {request.goal}
    - The other party, the AI, is simulating a {request.other_party}

    Format your output as a list of 'Recommendation' objects.
    Each recommendation represents a Pydantic model with two fields:
    - `heading`: A short title or summary of the recommendation
    - `text`: A description or elaboration of the recommendation

    Do not include markdown, explanation, or code formatting.

    Example Recommendations:
    1. heading: "Practice the STAR method", 
    text: "When giving feedback, use the Situation, Task, Action, Result framework to provide more 
    concrete examples."
    
    2. heading: "Ask more diagnostic questions", 
    text: "Spend more time understanding root causes before moving to solutions. 
    This builds empathy and leads to more effective outcomes."

    3. heading: "Define clear next steps",
    text: "End feedback conversations with agreed-upon action items, timelines, and follow-up plans.

    """

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are an expert communication coach analyzing training sessions.',
        model='gpt-4o-2024-08-06',
        output_model=RecommendationsCollection,
    )

    return response


def generate_and_store_feedback(
    session_id: str, example_request: ExamplesRequest, db: Session
) -> TrainingSessionFeedback:
    """
    Generate feedback based on session_id and transcript data,
    and write it to the training_session_feedback table
    """

    examples_request = example_request
    goals_request = GoalsAchievementRequest(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
    )
    recommendations_request = RecommendationsRequest(
        category=example_request.category,
        goal=example_request.goal,
        context=example_request.context,
        other_party=example_request.other_party,
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        key_concepts=example_request.key_concepts,
    )

    examples = generate_training_examples(examples_request)
    goals = get_achieved_goals(goals_request)
    recommendations = generate_recommendations(recommendations_request)
    print(examples, goals, recommendations)

    feedback = TrainingSessionFeedback(
        id=str(uuid4()),
        session_id=session_id,
        scores={},
        tone_analysis={},
        overall_score=None,
        transcript_uri=None,
        speak_time_percent=None,
        questions_asked=None,
        session_length_s=None,
        goals_achieved=len(goals.goals_achieved),
        examples_positive=examples.positive_examples,
        examples_negative=examples.negative_examples,
        recommendations=recommendations.recommendations,
        status=FeedbackStatusEnum.pending,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    db.add(feedback)
    db.commit()
    return feedback


if __name__ == '__main__':
    # Example usage of the service functions
    example_request = ExamplesRequest(
        category='Termination',
        goal='Successfully conduct a termination meeting',
        context='Termination meeting with a team member on poor performance',
        other_party='Team member',
        transcript='User:  Hi, I have to talk to you.'
        + "AI: Yes, what is it? Please don't fire me, I really need this job. "
        + "I know I haven't been performing well lately, but I promise I can improve. "
        + "I'll do whatever it takes."
        + 'Response interrupted'
        + "User:  I'm sorry but I'm not happy with your performance."
        + 'AI: I understand, and I take full responsibility. '
        + 'Could you please tell me specifically what areas I need to improve on?'
        + "I'm willing to work late, come in early, take on extra tasks—anything "
        + 'to meet your expectations. Just please give me a chance to prove myself.'
        + "User:  You can't do anything it's too late to improve."
        + "AI: Please, don't say that. I'm a hard worker, and I'm a quick learner."
        + "If you give me another chance, I promise I won't let you down."
        + 'Is there anything, anything at all, I can do to change your mind?',
        objectives=[
            'Bring clarity to the situation',
            'Encourage open dialogue',
            'Maintain professionalism',
            'Provide specific feedback',
            'Foster mutual understanding',
            'End on a positive note',
        ],
        key_concepts='### Active Listening\nShow empathy and paraphrase concerns.',
    )

    examples = generate_training_examples(example_request)

    if len(examples.positive_examples) == 0:
        print('No positive examples found. Please check the transcript and guidelines.')
    if len(examples.negative_examples) == 0:
        print('No negative examples found. Please check the transcript and guidelines.')

    for example in examples.positive_examples:
        print(f'Positive Example: {example.heading}')
        print(f'Text: {example.text}')
        print(f'Quote: {example.quote}')
        print(f'Guideline: {example.guideline}\n')

    for example in examples.negative_examples:
        print(f'Negative Example: {example.heading}')
        print(f'Text: {example.text}')
        print(f'Quote: {example.quote}')
        print(f'Improved Quote: {example.improved_quote}\n')

    print('Training examples generated successfully.')

    goals_achievement_request = GoalsAchievementRequest(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
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
    )
    recommendations = generate_recommendations(recommendation_request)
    for recommendation in recommendations.recommendations:
        print(f'Recommendation: {recommendation.heading}')
        print(f'Text: {recommendation.text}\n')
    print('Recommendations generated successfully.')

    generate_and_store_feedback('', example_request, None)
