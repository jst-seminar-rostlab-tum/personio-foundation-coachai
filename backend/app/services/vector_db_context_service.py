from app.rag.rag import build_vector_db_retriever
from app.rag.vector_db import format_docs
from app.schemas.training_preparation_schema import TrainingCaseBase


def build_query_prep_feedback(
    session_context: TrainingCaseBase, user_audio_analysis: str = None, user_transcript: str = None
) -> str:
    parts = []

    if session_context.category:
        parts.append(f'This is a {session_context.category}.')

    if session_context.other_party:
        parts.append(f'The HR employee is speaking to {session_context.other_party}.')

    if session_context.context:
        parts.append(f'The context is: {session_context.context}')

    if session_context.goal:
        parts.append(f'The goal is {session_context.goal}.')

    if user_transcript:
        parts.append(f'The HR employee said: {user_transcript}.')

    if user_audio_analysis:
        parts.append(f'It was spoken in the manner: {user_audio_analysis}.')

    return ' '.join(parts)


def build_query_general(
    other_context: [str] = None, user_audio_analysis: str = None, user_transcript: str = None
) -> str:
    parts = ['The general context is: '] + other_context

    if user_transcript:
        parts.append(f'The HR employee said: {user_transcript}.')

    if user_audio_analysis:
        parts.append(f'It was spoken in the manner: {user_audio_analysis}.')

    return ' '.join(parts)


def query_vector_db(
    session_context: TrainingCaseBase | [str] = None,
    user_audio_path: str = None,
    user_transcript: str = None,
) -> str:
    # TODO: Get from voice analysis function
    voice_analysis = user_audio_path
    if isinstance(session_context, TrainingCaseBase):
        query = build_query_prep_feedback(session_context, voice_analysis, user_transcript)
    else:
        query = build_query_general(session_context, voice_analysis, user_transcript)
    retriever = build_vector_db_retriever(populate_db=False)
    return format_docs(retriever.invoke(query))
