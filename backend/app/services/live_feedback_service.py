import concurrent.futures
from uuid import UUID

from sqlmodel import Session as DBSession
from sqlmodel import select
from tenacity import retry, stop_after_attempt, wait_fixed

from app.connections.openai_client import call_structured_llm
from app.models.live_feedback_model import LiveFeedback
from app.schemas import SessionTurnCreate
from app.schemas.live_feedback_schema import LiveFeedbackRead
from app.services.voice_analysis_service import analyze_voice_gemini_from_file


def format_feedback_lines(feedback_items: list[LiveFeedbackRead]) -> list[str]:
    return [f'{item.heading}: {item.feedback_text}' for item in feedback_items]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_generate_live_feedback_item(
    session_turn_context: SessionTurnCreate,
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
    user_audio_path: str = 'No audio available',
    transcript: str = 'No transcript available',
    previous_feedback: str = 'No previous feedback available',
    hr_docs_context: str = 'No hr document context available',
) -> LiveFeedback:
    voice_analysis = None
    if user_audio_path:
        voice_analysis = analyze_voice_gemini_from_file(user_audio_path)

    user_prompt = f"""
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

    return call_structured_llm(
        request_prompt=user_prompt,
        system_prompt=(
            'You are an expert communication coach analyzing a single speaking turn.'
            'Always respond in the language of the transcript.'
        ),
        model='gpt-4o-2024-08-06',
        output_model=LiveFeedback,
        mock_response=None,
    )


def fetch_all_for_session(db_session: DBSession, session_id: UUID) -> list[LiveFeedbackRead]:
    statement = (
        select(LiveFeedback)
        .where(LiveFeedback.session_id == session_id)
        .order_by(LiveFeedback.created_at)
    )
    feedback_items = db_session.exec(statement).all()
    return [LiveFeedbackRead(**item.model_dump()) for item in feedback_items]


def generate_and_store_live_feedback(
    db_session: DBSession, session_id: UUID, session_turn_context: SessionTurnCreate
) -> LiveFeedback | None:
    hr_docs_context = ''
    feedback_items = fetch_all_for_session(db_session, session_id)
    formatted_lines = format_feedback_lines(feedback_items)
    previous_feedback = '\n'.join(formatted_lines)

    if (
        not session_turn_context.audio_uri
        and not session_turn_context.text
        and not hr_docs_context
        and not previous_feedback
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
                live_feedback_item.session_id = session_id
            except Exception as e:
                print('[ERROR] Failed to generate live feedback:', e)
                return None

        db_session.add(live_feedback_item)
        db_session.commit()
        db_session.refresh(live_feedback_item)
        return live_feedback_item
