"""Service layer for voice analysis service."""

from app.connections.vertexai_client import call_llm_with_audio

prompt = (
    'The person speaking is a practicing HR employee in a test scenario. '
    "Describe the speaker's tone and speaking manner, "
    'e.g. emotion, stuttering, quietness, in this audio clip considering the context.'
    " Don't analyze what is said, rather how it's said. Be concise, use at most 2 sentences"
)


def analyze_voice(audio_uri: str) -> str:
    """
    Analyzes the tone and speaking manner of a speaker from an audio uri using Gemini via Vertex AI.
    The analysis focuses on vocal delivery rather than content.

    Parameters:
        audio_uri (str): The file uri.

    Returns:
        str: A concise textual analysis (max 2 sentences) describing the speaker's voice.
    """
    if not audio_uri:
        return ''
    return call_llm_with_audio(audio_uri=audio_uri, request_prompt=prompt)
