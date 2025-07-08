import concurrent.futures
import json
from uuid import UUID

from sqlmodel import Session as DBSession
from sqlmodel import select
from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.openai_client import call_structured_llm
from app.models import SessionTurn
from app.models.live_feedback_model import LiveFeedback as LiveFeedbackDB
from app.schemas.live_feedback_schema import LiveFeedback
from app.services.voice_analysis_service import analyze_voice_gemini_from_file


def fetch_all_for_session(db_session: DBSession, session_id: UUID) -> list[LiveFeedback]:
    statement = (
        select(LiveFeedbackDB)
        .where(LiveFeedbackDB.session_id == session_id)
        .order_by(LiveFeedbackDB.created_at)
    )
    feedback_items = db_session.exec(statement).all()
    return [
        LiveFeedback(heading=item.heading, feedback_text=item.feedback_text)
        for item in feedback_items
    ]


def format_feedback_lines(feedback_items: list[LiveFeedback]) -> list[str]:
    return [
        json.dumps({'heading': item.heading, 'feedback_text': item.feedback_text})
        for item in feedback_items
    ]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_live_feedback_item(
    session_turn_context: SessionTurn,
    previous_feedback: str = '',
    hr_docs_context: str = '',
) -> LiveFeedback:
    if previous_feedback is None:
        previous_feedback = []
    return generate_live_feedback_item(
        session_turn_context.audio_uri,
        session_turn_context.text,
        previous_feedback,
        hr_docs_context,
    )


def generate_live_feedback_item(
    user_audio_path: str = None,
    transcript: str = 'No transcript available',
    previous_feedback: str = 'No previous feedback available',
    hr_docs_context: str = 'No hr document context available',
) -> LiveFeedback:
    voice_analysis = ''
    if user_audio_path:
        voice_analysis = analyze_voice_gemini_from_file(user_audio_path)
    if not voice_analysis:
        voice_analysis = 'No voice analysis available.'

    user_prompt = f"""
    Analyze the provided HR documents, the transcript, and voice analysis from a
    single turn of an HR professional's training conversation.
    Based on the these, assess the HR professional’s tone and speech content.
    Then generate 1 feedback item they can apply in their next conversational turn to 
    improve their performance.

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
    1. Format your output as a 'LiveFeedback' object.
    Each live feedback item represents a Pydantic model with two fields:
    - `heading`: A short title or summary of the feedback item
    - `feedback_text`: A description or elaboration of the feedback item

    Do not include markdown, explanation, or code formatting.

    2. Generate EXACTLY 1 feedback item, which should be concise (1-10 words).
    3. For the heading, use categories like: Tone, Clarity, Engagement, Next Step, or Content.
    4. Each new feedback item should have a different heading from the previous 4 feedback items.
    5. Feedback must be consistent with prior suggestions.
    6. Avoid rephrasing or repeating previous feedback items when possible.
    7. Use active voice and no hedging, be specific if possible.
    e.g."Speak more calmly" instead of "Use a calmer tone" 

    ### Examples
    Feedback items in order of generating:
    1. {{"heading": "Tone", "feedback_text": "Speak more calmly." }}
    2. {{"heading": "Engagement", "feedback_text": "Acknowledge their emotions directly." }}
    3. {{"heading": "Content", "feedback_text": "State clear facts for bad performance." }}
    4. {{"heading": "Clarity", "feedback_text": "Replace vague phrases with specific outcomes." }}
    5. {{"heading": "Next Step", "feedback_text": "Ask them to complete any paperwork necessary."}}
    6. {{"heading": "Tone", "feedback_text": "Great tone – keep it up!" }}

    """

    return call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=(
            'You are an expert communication coach analyzing a single speaking turn.'
            'Always respond in the language of the transcript.'
        ),
        model='gpt-4o-2024-08-06',
        output_model=LiveFeedback,
        mock_response=LiveFeedback(heading='Tone', feedback_text='Speak more calmly.'),
    )


def generate_and_store_live_feedback(
    db_session: DBSession,
    session_id: UUID,
    session_turn_context: SessionTurn,
    hr_docs_context: str = '',
) -> LiveFeedback | None:
    feedback_items = fetch_all_for_session(db_session, session_id)
    formatted_lines = format_feedback_lines(feedback_items)
    previous_feedback = '\n'.join(formatted_lines)

    if not any(
        [
            session_turn_context.audio_uri,
            session_turn_context.text,
            hr_docs_context,
            previous_feedback,
        ]
    ):
        return None
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_live_feedback = executor.submit(
                safe_generate_live_feedback_item,
                session_turn_context,
                previous_feedback,
                hr_docs_context,
            )

            try:
                live_feedback_item = future_live_feedback.result()
            except Exception as e:
                print('[ERROR] Failed to generate live feedback:', e)
                return None

        live_feedback_item_db = LiveFeedbackDB(
            session_id=session_id,
            heading=live_feedback_item.heading,
            feedback_text=live_feedback_item.feedback_text,
        )
        db_session.add(live_feedback_item_db)
        db_session.commit()
        db_session.refresh(live_feedback_item_db)
        return live_feedback_item_db


if __name__ == '__main__':
    # Example usage
    user_transcript = (
        'The reason we have to let you go is, because we are not satisfied with your performance'
    )
    user_previous_feedback = '{"heading": "Tone", "feedback_text": "Speak calmly"}'
    live_feedback_item = generate_live_feedback_item(
        user_audio_path='example_audio.wav',
        transcript=user_transcript,
        previous_feedback=user_previous_feedback,
    )
    print('heading:', live_feedback_item.heading)
    print('feedback_text:', live_feedback_item.feedback_text)
