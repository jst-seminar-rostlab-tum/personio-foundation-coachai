import json
import unittest
from collections.abc import Generator
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel import Session as DBSession

from app.enums.speaker import SpeakerType
from app.models.live_feedback_model import LiveFeedback
from app.models.session_turn import SessionTurn
from app.schemas.live_feedback_schema import LiveFeedbackLlmOutput, LiveFeedbackRead
from app.services.live_feedback_service import (
    fetch_live_feedback_for_session,
    format_feedback_lines,
    generate_and_store_live_feedback,
)


class TestLiveFeedbackService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite:///:memory:')
        SQLModel.metadata.create_all(cls.engine)
        cls.SessionLocal = DBSession(cls.engine)

    def setUp(self) -> None:
        self.session: Session = self.SessionLocal

    def tearDown(self) -> None:
        self.session.rollback()
        self.session.close()

    def get_session_turn(self, session_id: UUID, make_empty: bool = False) -> SessionTurn:
        if make_empty:
            return SessionTurn(
                id=uuid4(),
                session_id=session_id,
                speaker=SpeakerType.user,
                start_offset_ms=0,
                end_offset_ms=0,
                full_audio_start_offset_ms=0,
                text='',
                audio_uri='',
                ai_emotion='neutral',
                created_at=datetime.now(),
            )
        return SessionTurn(
            id=uuid4(),
            session_id=session_id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=0,
            full_audio_start_offset_ms=0,
            text="Let's discuss the next step.",
            audio_uri='example_audio.wav',
            ai_emotion='neutral',
            created_at=datetime.now(),
        )

    def test_fetch_all_for_session_returns_items_in_order(self) -> None:
        session_id = uuid4()
        now = datetime.now()

        item1 = LiveFeedback(
            session_id=session_id,
            heading='Tone',
            feedback_text='Speak clearly.',
            created_at=now - timedelta(seconds=1),
        )
        item2 = LiveFeedback(
            session_id=session_id,
            heading='Clarity',
            feedback_text='Be more direct.',
            created_at=now,
        )

        self.session.add(item1)
        self.session.add(item2)
        self.session.commit()

        results: list[LiveFeedbackRead] = fetch_live_feedback_for_session(
            self.session, session_id, None
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].heading, 'Clarity')
        self.assertEqual(results[1].heading, 'Tone')

    def test_format_feedback_lines_returns_json_strings(self) -> None:
        feedback_items = [
            LiveFeedbackRead(id=uuid4(), heading='Tone', feedback_text='Speak more calmly.'),
            LiveFeedbackRead(
                id=uuid4(), heading='Content', feedback_text='Be more specific with your request.'
            ),
        ]

        formatted = format_feedback_lines(feedback_items)

        # Check length
        self.assertEqual(len(formatted), 2)

        # Check that all items are valid JSON strings and match expected structure
        for original, json_string in zip(feedback_items, formatted, strict=False):
            parsed = json.loads(json_string)
            self.assertIsInstance(parsed, dict)
            self.assertEqual(parsed['heading'], original.heading)
            self.assertEqual(parsed['feedback_text'], original.feedback_text)

    @patch('app.services.live_feedback_service.analyze_voice')
    @patch('app.services.live_feedback_service.call_structured_llm')
    def test_generate_and_store_live_feedback_success(
        self, mock_call_structured_llm: MagicMock, mock_analyze_voice: MagicMock
    ) -> None:
        session_id = uuid4()

        session_turn_context = self.get_session_turn(session_id)
        mock_language_code = MagicMock()
        mock_language_code.name = 'de'
        mock_scenario = MagicMock()
        mock_scenario.language_code = mock_language_code
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.scenario = mock_scenario
        session_turn_context.session = mock_session

        mock_feedback = LiveFeedbackLlmOutput(
            heading='Tone',
            feedback_text='Speak more calmly.',
        )

        mock_return_value_audio = 'The speaker is nervous and speaking fast.'
        mock_analyze_voice.return_value = mock_return_value_audio
        mock_call_structured_llm.return_value = mock_feedback

        def mock_session_generator_func() -> Generator[Any, None, None]:
            yield self.session

        result = generate_and_store_live_feedback(
            mock_session_generator_func, session_id, session_turn_context
        )
        stored_items = self.session.exec(
            select(LiveFeedback).where(LiveFeedback.session_id == session_id)
        ).all()

        # Check result of generate_and_store_live_feedback
        self.assertIsNotNone(result)
        self.assertEqual(result.heading, 'Tone')
        self.assertEqual(result.feedback_text, 'Speak more calmly.')
        self.assertEqual(result.session_id, session_id)

        # Check the prompt passed to LLM
        args, kwargs = mock_call_structured_llm.call_args
        prompt_arg = kwargs.get('request_prompt')
        sys_prompt_arg = kwargs.get('system_prompt')
        self.assertIn(session_turn_context.text, prompt_arg)
        self.assertIn(mock_return_value_audio, prompt_arg)
        self.assertIn('de', sys_prompt_arg)

        # Check DB
        self.assertEqual(len(stored_items), 1)
        self.assertEqual(stored_items[0].heading, 'Tone')
        self.assertEqual(stored_items[0].feedback_text, 'Speak more calmly.')

    def test_generate_and_store_live_feedback_empty_turn_context(self) -> None:
        session_id = uuid4()
        session_turn_context = self.get_session_turn(session_id, make_empty=True)

        def mock_session_generator_func() -> Generator[Any, None, None]:
            yield self.session

        result = generate_and_store_live_feedback(
            mock_session_generator_func, session_id, session_turn_context
        )

        self.assertIsNone(result)
