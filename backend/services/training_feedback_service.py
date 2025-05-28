from backend.connections.openai_client import call_structured_llm
from backend.schemas.training_feedback_schema import (
    ExamplesRequest,
    GoalAchieved,
    GoalAchievementRequest,
    RecommendationsCollection,
    RecommendationsRequest,
    TrainingExamplesCollection,
)


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

    Format your output as a Pydantic model with two fields:
    - `positive_examples`: a Markdown string listing up to 3 positive examples.
    - `negative_examples`: a Markdown string listing up to 3 negative examples.

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


def get_achieved_goals(request: GoalAchievementRequest) -> int:
    user_prompt = f"""
    The following is a transcript of a training session.
    Please evaluate how many of the listed goals were clearly achieved by the user 
    in this conversation.

    Transcript:
    {request.transcript}

    Goals:
    {request.objectives}

    Instructions:
    - For each goal, determine if the user’s speech aligns with 
        and fulfills the intention behind it.
    - Only count goals that are clearly demonstrated in the user's statements.
    - Return the number of goals achieved as an integer.
    """

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are an expert communication coach analyzing training sessions.',
        model='gpt-4o-2024-08-06',
        output_model=GoalAchieved,
    )

    return response.goals_achieved


def generate_recommendations(request: RecommendationsRequest) -> RecommendationsCollection:
    user_prompt = f"""
    Analyze the following transcript from a training session.
    Based on the goal, objectives, and key concepts, suggest 3 to 5 specific, actionable 
    communication improvement recommendations for the user.

    Each recommendation should:
    - Be based directly on how the user performed in the transcript
    - Be short, specific, and actionable
    - Be written as a single Markdown string that includes:
    - A header using the format #### Recommendation Title
    - A short paragraph explaining what to improve and how

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

    Format your output as a list of objects.
    Do not include any markdown formatting outside of the recommendation strings. 
    Only return the list of structured `Recommendation` objects, ready to be parsed into the 
    `RecommendationsCollection` model.
    """

    response = call_structured_llm(
        request_prompt=user_prompt,
        system_prompt='You are an expert communication coach analyzing training sessions.',
        model='gpt-4o-2024-08-06',
        output_model=RecommendationsCollection,
    )

    return response


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

    print(f'Positive Examples: {examples.positive_examples}')

    print(f'Negative Examples: {examples.negative_examples}')

    print('Training examples generated successfully.')

    goals_achievement_request = GoalAchievementRequest(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
    )
    goals_achieved = get_achieved_goals(goals_achievement_request)
    print(f'Number of goals achieved: {goals_achieved} / {len(example_request.objectives)}')

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
        print(f'Recommendation: {recommendation.markdown}')
