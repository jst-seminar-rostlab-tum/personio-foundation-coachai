def build_training_examples_prompt(
    category: str,
    transcript: str | None,
    objectives: list,
    persona: str,
    situational_facts: str,
    key_concepts: str,
    hr_docs_context: str = '',
) -> str:
    """
    Builds a user prompt for extracting positive and negative examples
    from a training session transcript.

    Args:
        category (str): The conversation or training context/category.
        transcript (str): The full transcript of the session.
        objectives (list): List of objectives for the training.
        persona (str): The persona description including training focus.
        situational_facts (str): Key situational facts of the session.
        key_concepts (str): Key concepts relevant to the session.
        hr_docs_context (str, optional): Additional HR document context.

    Returns:
        str: The constructed prompt string.
    """
    return f"""
    The following is a training session transcript in which you are practicing 
    communication skills in the context of {category}. 
    You are expected to follow the training guidelines provided below.
    The AI simulates the other party in the conversation, and you are expected to respond
    appropriately based on the training objectives, the persona you're speaking to 
    and the respective training focus, the situational facts, and the key concepts.

    **Speaker labels in the transcript:**
    - Lines starting with **"User:"** are your own statements.
    - Lines starting with **"Assistant:"** are the AI's responses and are for context only.

    Transcript:
    {transcript}

    If an audio file is provided (audio_uri), you may use both the transcript and the audio content 
    to inform your analysis. The audio may contain additional context or nuances 
    not captured in the transcript.

    Training Guidelines:
    - Objectives: {objectives}
    - Persona incl. Training focus: {persona}
    - Situational Facts: {situational_facts}
    - Key Concepts: {key_concepts}

    HR Document Context:
    {hr_docs_context}

    Instructions:
    Carefully analyze the provided transcript and evaluate **only your own statements** 
    (what you said as the User).  
    **Do not analyze, quote, or critique any statements made by the Assistant.**  
    The Assistant's lines are for context only.

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
    """.strip()


def build_goals_achieved_prompt(
    transcript: str | None,
    objectives: list[str],
    hr_docs_context: str = '',
) -> str:
    """
    Builds a user prompt for evaluating which goals were achieved by the user in a session.

    Args:
        transcript (str, optional): The session transcript. Defaults to empty string if None.
        objectives (list, optional): List of goals/objectives.
        hr_docs_context (str, optional): Additional HR document context.

    Returns:
        str: The constructed prompt string.
    """
    transcript_text = transcript or ''
    objectives_text = objectives if objectives is not None else []

    return f"""
    The following is a transcript of a training session.
    Please evaluate which of the listed goals were clearly achieved by the user 
    in this conversation.

    Transcript:
    {transcript_text}

    If an audio file is provided (audio_uri), you may use both the transcript and the audio content 
    to inform your analysis. The audio may contain additional context or nuances 
    not captured in the transcript.

    Goals:
    {objectives_text}
        
    HR Document Context:
    {hr_docs_context}

    Instructions:
    - For each goal, determine if the user's speech aligns with 
        and fulfills the intention behind it.
    - Only count goals that are clearly demonstrated in the user's statements.
    - Only mark a goal as achieved if there is clear and explicit evidence in the User's utterances.
    - Do not infer or assume achievement based on general conversation or politeness.
    - If the User does not directly address a goal, do not mark it as achieved.

    - Format your output as a list of strings, where each string is a goal that was achieved.
    - Do not include any additional commentary or formatting.
    - Only return the list of achieved goals, not the entire transcript or any other text.
    - If no goals were achieved, return an empty list.
    - If some goals were achieved, return a list of those goals.
    - If all goals were achieved, return the full list of goals.
    - Do not include any markdown formatting or extra text.
    """.strip()


def build_recommendations_prompt(
    transcript: str | None,
    objectives: list[str],
    persona: str = '',
    key_concepts: str = '',
    situational_facts: str = '',
    category: str = '',
    hr_docs_context: str = '',
) -> str:
    """
    Builds a user prompt for generating actionable communication improvement recommendations.

    Args:
        transcript (str, optional): Session transcript.
        persona (str, optional): Persona description and training focus.
        objectives (list, optional): List of objectives.
        key_concepts (str, optional): Key concepts for the session.
        situational_facts (str, optional): Relevant situational facts.
        category (str, optional): Conversation/training category.
        hr_docs_context (str, optional): Additional HR document context.

    Returns:
        str: The constructed prompt string.
    """
    transcript_text = transcript or ''
    objectives_text = objectives if objectives is not None else []

    return f"""
    Analyze the following transcript from a training session.
    Based on the goal, objectives, and key concepts, suggest 3 to 5 specific, actionable 
    communication improvement recommendations for the user.

    Each recommendation should:
    - Be based directly on how the user performed in the transcript
    - Be short, specific, and actionable

    Transcript:
    {transcript_text}

    If an audio file is provided (audio_uri), you may use both the transcript and the audio content 
    to inform your analysis. The audio may contain additional context or nuances 
    not captured in the transcript.

    Persona (other party) including Training Focus:
    {persona}

    Objectives:
    {objectives_text}

    Key Concepts:
    {key_concepts}

    Situational Facts:
    {situational_facts}
        
    HR Document Context:
    {hr_docs_context}

    Situation:
    - The conversation of this training session is about {category}
    - The other party, the AI, is simulating the following persona, which 
    focuses on the specified training areas: {persona}

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
    """.strip()
