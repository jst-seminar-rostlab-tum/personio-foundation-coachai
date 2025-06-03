from ..connections.gemini_client import generate_llm_content


def analyze_audio(audio_uri: str) -> str:
    # TODO: Exchange this with real functionality, this is a placeholder
    return "The person's speaking tone was clear and confident, but not rude."


def generate_real_time_feedback(
    audio_uri: str,
    transcript: str,
    previous_feedback: str,  # Only using previous feedback to avoid huge prompts
    vector_db_retrieved_docs: str,
) -> str:
    voice_analysis = analyze_audio(audio_uri)
    prompt = f"""
    You are an assistant that gives short, helpful feedback (1–5 words) to a practicing HR employee
    based on their spoken behavior. 
    Use the HR guidelines, the transcript, and voice analysis below to assess their tone, content,
    and suggest next steps.

    ### Context
    HR Guidelines:
    {vector_db_retrieved_docs}

    Transcript:
    "{transcript}"

    Voice Analysis:
    {voice_analysis}

    Previous Feedback:
    {previous_feedback}

    ### Instructions
    1. Generate new feedback in the format: "<Category>: <Short feedback>".
    2. Use categories like: Tone, Clarity, Engagement, Next Step, or Content.
    3. Do NOT repeat or rephrase previous feedback.
    4. Feedback must be consistent with prior suggestions.
    5. Maximum of 3 feedback lines. Each line should be concise (1–5 words).

    ### Output
    New Feedback:
    """

    return generate_llm_content(prompt=prompt)
