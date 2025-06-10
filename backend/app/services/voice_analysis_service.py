import os
import tempfile

import requests

from app.connections.gemini_client import generate_gemini_content, upload_audio_gemini

prompt = (
    'The person speaking is a practicing HR employee in a test scenario. '
    "Describe the speaker's tone and speaking manner, "
    'e.g. emotion, stuttering, quietness, in this audio clip considering the context.'
    " Don't analyze what is said, rather how it's said. Be concise, use at most 2 sentences"
)


def analyze_voice_gemini_from_file(audio_path: str) -> str:
    """
    Analyzes the tone and speaking manner of a speaker from a local audio file using Gemini AI.
    The analysis focuses on vocal delivery rather than content.

    Args:
        audio_path (str): The file path to the local audio file.

    Returns:
        str: A concise textual analysis (max 2 sentences) describing the speaker's voice.
    """
    if not os.path.exists(audio_path):
        print(f'Audio file not found at: {audio_path}')
    myfile = upload_audio_gemini(audio_path=audio_path)
    response_text = generate_gemini_content(contents=[prompt, myfile])

    return response_text


def analyze_voice_gemini_from_uri(audio_uri: str, audio_format: str = 'mp3') -> str:
    """
    Downloads an audio file from a URI and
    analyzes the speaker's tone and speaking manner using Gemini AI.

    The file is temporarily saved locally before analysis.
    The analysis focuses on vocal delivery rather than content.

    Args:
        audio_uri (str): The URL pointing to the audio file to analyze.
        audio_format (str, optional): The format/extension of the audio file (default is 'mp3').

    Returns:
        str: A concise textual analysis (max 2 sentences) describing the speaker's delivery.
    """
    tmp_file_path = None

    try:
        response = requests.get(audio_uri)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file.flush()
            tmp_file_path = tmp_file.name

        return analyze_voice_gemini_from_file(tmp_file_path)

    except Exception as e:
        print(f'Audio analysis failed: {e}')

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception as e:
                print(f'Could not delete temporary file {tmp_file_path}: {e}')
