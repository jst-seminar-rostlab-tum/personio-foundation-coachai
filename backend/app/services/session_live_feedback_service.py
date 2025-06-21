from app.services.voice_analysis_service import analyze_voice_gemini_from_file


def generate_live_feedback(
    user_audio_path: str,
    transcript: str,
    previous_feedback: str,
    hr_docs_context: str,
) -> str:
    voice_analysis = None
    if user_audio_path:
        voice_analysis = analyze_voice_gemini_from_file(user_audio_path)

    # user_prompt = \
    f"""
    Analyze the provided HR documents, the transcript, and voice analysis from a
    single turn of an HR professional's training conversation.
    Based on the these, assess the HR professional’s tone and speech content. Then suggest concise 
    next steps (1–10 words each) they can apply in their next conversational turn to improve their
    performance.

    ### Context
    HR Document Context:
    {hr_docs_context}

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

    return ''
    # return call_structured_llm(
    #     request_prompt=user_prompt,
    #     system_prompt='You are an expert communication coach analyzing training sessions.',
    #     model='gpt-4o-2024-08-06',
    #     output_model=None,
    #     mock_response=mock_response,
    # )
