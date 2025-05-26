from backend.connections.openai_client import get_client
from backend.schemas.training_feedback_schema import (
    TrainingExamplesCollection,
    TrainingFeedbackRequest,
)

client = get_client()


def invoke_llm(user_prompt: str) -> str:
    response = client.chat.completions.create(
        model='gpt-4o-2024-08-06',
        messages=[
            {
                'role': 'system',
                'content': 'You are an expert communication coach analyzing training sessions.',
            },
            {'role': 'user', 'content': user_prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    return response.choices[0].message.content.strip()


def generate_training_examples(request: TrainingFeedbackRequest) -> TrainingExamplesCollection:
    user_prompt = f"""
    The following is a training session transcript, in which the user is practicing 
    communication skills in the context of {request.category}. 
    The user is expected to follow the training guidelines provided below.
    The ai simulates the other party in the conversation, and the user is expected to respond
    appropriately based on the training objectives, goal, context, and key concepts.
    In this case, the user is practicing how to {request.goal} in the context of {request.context}.
    The other party, the AI, is simulating a {request.other_party}.

    Transcript:
    {request.transcript}

    Training Guidelines:
    - Objectives: {request.objectives}
    - Goal: {request.goal}
    - Context: {request.context}
    - Key Concepts: {request.key_concepts}
    
    Instructions:
    Analyze the provided transcript and how the user performed against the training guidelines. 
    Extract up to 5 positive and 5 negative examples comparing the user's performance to the 
    provided training guidelines. Only extract examples that are said from the user, not the AI.
    Your output is shown to the user to help them improve their communication skills. 
    So instead of saying "the user", use "you" to refer to the user.

    Return JSON only structured like this:
    {{
        "positive_examples": [
            {{ "heading": "...", "text": "...", "quote": "...", "guideline": "..." }}
        ],
        "negative_examples": [
            {{ "heading": "...", "text": "...", "quote": "...", "improved_quote": "..." }}
        ]
    }}
    Do not include markdown or ```json formatting.
    """

    response = invoke_llm(user_prompt)

    return TrainingExamplesCollection.model_validate_json(response)


if __name__ == '__main__':
    # Example usage of the generate_training_examples function
    example_request = TrainingFeedbackRequest(
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

    for example in examples.positive_examples:
        print(f'Positive Example: {example.heading}')
        print(f'Text: {example.text}')
        print(f"Quote: '{example.quote}'")
        print(f'Guideline: {example.guideline}\n')

    for example in examples.negative_examples:
        print(f'Negative Example: {example.heading}')
        print(f'Text: {example.text}')
        print(f"Quote: '{example.quote}'")
        print(f"Improved Quote: '{example.improved_quote}'\n")

    print('Training examples generated successfully.')
