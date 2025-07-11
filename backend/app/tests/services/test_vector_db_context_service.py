import unittest
from unittest.mock import MagicMock, patch

from langchain.schema import Document

from app.schemas.conversation_scenario import ConversationScenarioAIPromptRead
from app.services.vector_db_context_service import (
    build_query_general,
    build_query_prep_feedback,
    query_vector_db,
    query_vector_db_and_prompt,
)


class TestVectorDbContextService(unittest.TestCase):
    def test_build_query_prep_feedback_all_fields(self) -> None:
        session = ConversationScenarioAIPromptRead(
            category_name='Performance Review',
            persona='Intern',
            situational_facts='Annual evaluation meeting',
        )
        transcript = 'I appreciate your hard work this year'
        audio_analysis = 'calm and encouraging'

        result = build_query_prep_feedback(session, audio_analysis, transcript)

        expected = (
            'This is a/an Performance Review. '
            'The HR employee is speaking to Intern. '
            'The context is: Annual evaluation meeting '
            'The HR employee said: I appreciate your hard work this year. '
            'It was spoken in the manner: calm and encouraging.'
        )
        self.assertEqual(result, expected)

    def test_build_query_general_all_fields(self) -> None:
        other_ctx = ['Company policies', 'Team structure']
        transcript = 'Welcome to the team'
        audio_analysis = 'upbeat'

        result = build_query_general(other_ctx, audio_analysis, transcript)

        expected = (
            'The general context is:  Company policies Team structure '
            'The HR employee said: Welcome to the team. '
            'It was spoken in the manner: upbeat.'
        )
        self.assertEqual(result, expected)

    def test_build_query_general_empty(self) -> None:
        # no inputs => empty string
        assert build_query_general([]) == ''
        assert build_query_general(None, None, None) == ''

    @patch('app.services.vector_db_context_service.build_vector_db_retriever')
    @patch('app.services.vector_db_context_service.analyze_voice')
    def test_query_vector_db_with_structured_context(
        self, mock_analyze: MagicMock, mock_retriever_builder: MagicMock
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
        scenario = ConversationScenarioAIPromptRead(
            category_name='Coaching',
            persona='Jacob. Training Focus: Set growth plan. Company Position: Intern',
            situational_facts='Career development',
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
        self.assertEqual(text, doc_content)
        self.assertEqual(metadata, [doc_metadata])

    @patch('app.services.vector_db_context_service.build_vector_db_retriever')
    @patch('app.services.vector_db_context_service.analyze_voice')
    def test_query_vector_db_complex(
        self, mock_analyze: MagicMock, mock_retriever_builder: MagicMock
    ) -> None:
        # Prepare audio and transcript
        audio_path = None
        transcript = 'We need to adapt as soon as possible.'

        # Prepare retriever and docs
        fake_retriever = MagicMock()
        doc_content_1 = 'Prepare team for adapting.'
        doc_metadata_1 = {'source': 'doc1'}
        document_1 = Document(page_content=doc_content_1, metadata=doc_metadata_1)
        doc_content_2 = 'Bring up the topic soon.'
        doc_metadata_2 = {'source': 'doc2'}
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
        mock_retriever_builder.assert_called_once()
        fake_retriever.invoke.assert_called_once_with(expected_query)
        self.assertFalse(mock_analyze.called)
        self.assertEqual(text, doc_content_1 + '\n\n' + doc_content_2)
        self.assertEqual(metadata, [doc_metadata_1, doc_metadata_2])

    @patch('app.services.vector_db_context_service.query_vector_db')
    def test_query_vector_db_and_prompt_with_results(self, mock_query_vector_db: MagicMock) -> None:
        # Set up args and mocks
        generated_object = 'objectives'
        session_context = ['Example context']
        transcript = "Here's a user statement."

        doc1 = 'Follow the company policy.'
        doc2 = 'Ensure respectful communication.'
        combined_docs = f'{doc1}\n\n{doc2}'
        mock_query_vector_db.return_value = (
            combined_docs,
            [{'source': 'doc1'}, {'source': 'doc2'}],
        )

        result, doc_names = query_vector_db_and_prompt(
            generated_object=generated_object,
            session_context=session_context,
            user_transcript=transcript,
        )

        # Assert
        expected = (
            f'\nThe objectives you generate should comply with '
            f'the following HR Guideline excerpts:\n'
            f'{combined_docs}\n'
        )
        mock_query_vector_db.assert_called_once()
        self.assertEqual(result, expected)

    @patch('app.services.vector_db_context_service.query_vector_db')
    def test_query_vector_db_and_prompt_with_none(self, mock_query_vector_db: MagicMock) -> None:
        # Set up args and mocks
        generated_object = 'objectives'
        mock_query_vector_db.return_value = (None, None)

        result, doc_names = query_vector_db_and_prompt(
            generated_object=generated_object, session_context=None, user_transcript=None
        )

        # Assert
        assert result == ''
        mock_query_vector_db.assert_called_once()

    @patch('app.services.vector_db_context_service.query_vector_db')
    def test_query_vector_db_and_prompt_with_empty_docs(
        self, mock_query_vector_db: MagicMock
    ) -> None:
        # Set up args and mocks
        generated_object = 'objectives'
        mock_query_vector_db.return_value = ('', [])

        result, doc_names = query_vector_db_and_prompt(
            generated_object=generated_object, session_context=None, user_transcript=None
        )

        # Assert
        self.assertEqual(result, '')
        mock_query_vector_db.assert_called_once()
