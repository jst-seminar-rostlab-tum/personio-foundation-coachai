from unittest.mock import MagicMock, patch

from langchain.schema import Document

from app.schemas.scenario_preparation_schema import ConversationScenarioBase
from app.services.vector_db_context_service import (
    build_query_general,
    build_query_prep_feedback,
    query_vector_db,
)


def test_build_query_prep_feedback_all_fields() -> None:
    session = ConversationScenarioBase(
        category='Performance Review',
        other_party='Intern',
        context='Annual evaluation meeting',
        goal='Provide balanced feedback',
    )
    transcript = 'I appreciate your hard work this year'
    audio_analysis = 'calm and encouraging'

    result = build_query_prep_feedback(session, audio_analysis, transcript)

    expected = (
        'This is a/an Performance Review. '
        'The HR employee is speaking to Intern. '
        'The context is: Annual evaluation meeting '
        'The goal is Provide balanced feedback. '
        'The HR employee said: I appreciate your hard work this year. '
        'It was spoken in the manner: calm and encouraging.'
    )
    assert result == expected


def test_build_query_general_all_fields() -> None:
    other_ctx = ['Company policies', 'Team structure']
    transcript = 'Welcome to the team'
    audio_analysis = 'upbeat'

    result = build_query_general(other_ctx, audio_analysis, transcript)

    expected = (
        'The general context is:  Company policies Team structure '
        'The HR employee said: Welcome to the team. '
        'It was spoken in the manner: upbeat.'
    )
    assert result == expected


def test_build_query_general_empty() -> None:
    # no inputs => empty string
    assert build_query_general([]) == ''
    assert build_query_general(None, None, None) == ''


@patch('app.services.vector_db_context_service.build_vector_db_retriever')
@patch('app.services.vector_db_context_service.analyze_voice_gemini_from_file')
def test_query_vector_db_with_structured_context(
    mock_analyze: MagicMock, mock_retriever_builder: MagicMock
) -> None:
    # Prepare audio and transcript
    audio_path = '/tmp/audio.wav'
    mock_analyze.return_value = 'friendly tone'

    transcript = "Let's set some goals"

    # Prepare retriever and docs
    fake_retriever = MagicMock()
    doc_content = 'Set goals'
    doc_metadata = {'source': 'https://example.com'}
    document = Document(page_content=doc_content, metadata=doc_metadata)
    fake_docs = [document]
    fake_retriever.invoke.return_value = fake_docs
    mock_retriever_builder.return_value = fake_retriever

    # Set up conversation scenario
    scenario = ConversationScenarioBase(
        category='Coaching',
        other_party='Junior employee',
        context='Career development',
        goal='Set growth plan',
    )

    # Build expected values and results
    expected_query = build_query_prep_feedback(scenario, mock_analyze.return_value, transcript)
    text, metadata = query_vector_db(
        scenario, user_audio_path=audio_path, user_transcript=transcript
    )

    # Assert
    mock_analyze.assert_called_once_with(audio_path)
    mock_retriever_builder.assert_called_once()
    fake_retriever.invoke.assert_called_once_with(expected_query)
    assert text == doc_content
    assert metadata == [doc_metadata]


@patch('app.services.vector_db_context_service.build_vector_db_retriever')
@patch('app.services.vector_db_context_service.analyze_voice_gemini_from_file')
def test_query_vector_db_complex(
    mock_analyze: MagicMock, mock_retriever_builder: MagicMock
) -> None:
    # Prepare audio and transcript
    audio_path = None
    transcript = 'We need to adapt as soon as possible.'

    # Prepare retriever and docs
    fake_retriever = MagicMock()
    doc_content_1 = 'Prepare team for adapting.'
    doc_metadata_1 = {'source': 'https://example.com'}
    document_1 = Document(page_content=doc_content_1, metadata=doc_metadata_1)
    doc_content_2 = 'Bring up the topic soon.'
    doc_metadata_2 = {'source': 'https://example.com'}
    document_2 = Document(page_content=doc_content_2, metadata=doc_metadata_2)
    fake_docs = [document_1, document_2]
    fake_retriever.invoke.return_value = fake_docs
    mock_retriever_builder.return_value = fake_retriever

    # Set up conversation scenario
    other_context = ['Budget constraints', 'Timeline pressure']

    # Build expected values and results
    expected_query = build_query_general(other_context, None, transcript)
    text, metadata = query_vector_db(
        other_context, user_audio_path=audio_path, user_transcript=transcript
    )

    # Assert
    mock_analyze.assert_not_called()
    mock_retriever_builder.assert_called_once()
    fake_retriever.invoke.assert_called_once_with(expected_query)
    assert text == doc_content_1 + '\n\n' + doc_content_2
    assert metadata == [doc_metadata_1, doc_metadata_2]
