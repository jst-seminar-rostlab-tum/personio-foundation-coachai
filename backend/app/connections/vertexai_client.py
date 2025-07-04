import os
from typing import Any, TypeVar

from google import genai
from google.genai.types import GenerateContentConfig, Part
from openai import BaseModel

from app.config import Settings

settings = Settings()

DEFAULT_CHEAP_MODEL = 'gemini-2.0-flash-001'
# TODO: Change to 2.5, maybe?
# TODO: Add to env variables on GitHub too
FORCE_CHEAP_MODEL = settings.FORCE_CHEAP_MODEL
VERTEXAI_CRED_PATH = settings.VERTEXAI_CRED
VERTEXAI_PROJECT = settings.VERTEXAI_PROJECT
VERTEXAI_LOCATION = settings.VERTEXAI_LOCATION

key_path = os.path.abspath(VERTEXAI_CRED_PATH)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

if not VERTEXAI_CRED_PATH:
    print(
        '[WARNING] VERTEX_AI_CRED is missing or invalid. '
        'AI features will be disabled and mock responses will be used.'
    )
    ENABLE_AI = False
    vertexai_client = None
else:
    ENABLE_AI = settings.ENABLE_AI
    vertexai_client = genai.Client(
        vertexai=True, project=VERTEXAI_PROJECT, location=VERTEXAI_LOCATION
    )


def generate_content_vertexai(contents: [Any], model: str = DEFAULT_CHEAP_MODEL) -> str:
    if not ENABLE_AI or vertexai_client is None:
        print('Cannot upload files to Gemini, AI is disabled')
        return ''
    if None in contents:
        print('None found in Gemini contents')
        return ''
    try:
        response = vertexai_client.models.generate_content(model=model, contents=contents)
        return response.text
    except Exception as e:
        print(f'Gemini content generation failed: {e}')


def upload_audio_vertexai(audio_uri: str) -> Part:
    if not ENABLE_AI or vertexai_client is None:
        print('Cannot upload files to Gemini, AI is disabled')
    try:
        part = Part.from_uri(file_uri=audio_uri)
        return part
    except Exception as e:
        print(f"Error uploading audio file '{audio_uri}': {e}")


T = TypeVar('T', bound=BaseModel)


def call_structured_llm_vertexai(
    request_prompt: str,
    output_model: type[T],
    system_prompt: str | None = None,
    model: str = DEFAULT_CHEAP_MODEL,
    temperature: float = 1,
    max_tokens: int = 500,
    mock_response: T | None = None,
) -> T:
    if not ENABLE_AI or vertexai_client is None:
        if not mock_response:
            raise ValueError('AI is disabled and no mock response provided')
        return mock_response

    selected_model = DEFAULT_CHEAP_MODEL if FORCE_CHEAP_MODEL else (model or DEFAULT_CHEAP_MODEL)
    response = vertexai_client.models.generate_content(
        model=selected_model,
        contents=request_prompt,
        config=GenerateContentConfig(
            systemInstruction=system_prompt,
            temperature=temperature,
            maxTokens=max_tokens,
            responseSchema=output_model,
            # responseJsonSchema=output_model.model_json_schema()
            # responseMimeType=
        ),
    )

    return response.text


# example_request = ExamplesRequest(
#         category='Termination',
#         persona=(
#             '**Name**: Julian '
#             '**Training Focus**: Successfully conduct a termination meeting '
#             '**Company Position**: Team member'
#         ),
#         situational_facts='Termination meeting with a team member on poor performance',
#         transcript='User:  Hi, I have to talk to you. \n'
#         + "Assistant: Yes, what is it? Please don't fire me, I really need this job. "
#         + "I know I haven't been performing well lately, but I promise I can improve."
#         + "I'll do whatever it takes."
#         + 'Response interrupted'
#         + "User:  I'm sorry but I'm not happy with your performance. \n"
#         + 'Assistant: I understand, and I take full responsibility. \n'
#         + 'Could you please tell me specifically what areas I need to improve on?'
#         + "I'm willing to work late, come in early, take on extra tasks—anything "
#         + 'to meet your expectations. Just please give me a chance to prove myself. \n'
#         + "User:  You can't do anything it's too late to improve. \n"
#         + "Assistant: Please, don't say that. I'm a hard worker, "
#         "and I'm a quick learner."
#         + "If you give me another chance, I promise I won't let you down."
#         + 'Is there anything, anything at all, I can do to change your mind? \n',
#         objectives=[
#             'Bring clarity to the situation',
#             'Encourage open dialogue',
#             'Maintain professionalism',
#             'Provide specific feedback',
#             'Foster mutual understanding',
#             'End on a positive note',
#         ],
#         key_concepts='### Active Listening\nShow empathy and paraphrase concerns.',
#         language_code=LanguageCode.de,
#     )
#
# print("Model config", example_request.model_config)
# print("JSON", example_request.json)
# print("Schema JSON", example_request.model_json_schema())
