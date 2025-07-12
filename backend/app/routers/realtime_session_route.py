from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.config import settings
from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.session import Session, SessionStatus
from app.models.user_profile import UserProfile
from app.services.realtime_session_service import RealtimeSessionService

router = APIRouter(prefix='', tags=['realtime-session'])

if settings.FORCE_CHEAP_MODEL:
    MODEL = 'gpt-4o-mini-realtime-preview-2024-12-17'
else:
    MODEL = 'gpt-4o-realtime-preview-2025-06-03'


def get_realtime_session_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> RealtimeSessionService:
    """
    Dependency factory to inject the RealtimeSessionService.
    """
    return RealtimeSessionService(db_session)


@router.get('/realtime-session/{session_id}')
async def get_realtime_session(
    db_session: Annotated[DBSession, Depends(get_db_session)],
    user_profile: Annotated[UserProfile, Depends(require_user)],
    session_id: UUID,
) -> dict:
    """
    Proxies a POST request to OpenAI's realtime sessions endpoint
    and returns the JSON response.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='OPENAI_API_KEY not set'
        )

    session = db_session.exec(select(Session).where(Session.id == session_id)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
    if session.status is SessionStatus.completed:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, detail='Session is already completed'
        )

    conversation_scenario = db_session.exec(
        select(ConversationScenario).where(ConversationScenario.id == session.scenario_id)
    ).first()
    if not conversation_scenario:
        raise HTTPException(
            status_code=404, detail='No conversation scenario found for this session'
        )

    conversation_category = None
    if conversation_scenario.category_id:
        conversation_category = db_session.exec(
            select(ConversationCategory).where(
                ConversationCategory.id == conversation_scenario.category_id
            )
        ).first()
        if not conversation_category:
            raise HTTPException(
                status_code=404, detail='No conversation category found for this scenario'
            )

    conversation_category_name = None
    if conversation_category:
        conversation_category_name = conversation_category.name
    elif conversation_scenario.custom_category_label:
        conversation_category_name = conversation_scenario.custom_category_label
    else:
        conversation_category_name = 'Custom Conversation'

    instructions = (
        f"Your user wants to practice conversations about '{conversation_category_name}'. "
        f'Your job is to simulate the other party in that conversation.\n'
        f'Therefore adopt the following persona:\n {conversation_scenario.persona}\n\n'
        f'Stay in that character, respond naturally, and encourage realistic dialogue.'
        f'To have a better understanding of the background of the conversation about'
        f"'{conversation_category_name}' here are some more background informations:"
        f'{conversation_scenario.situational_facts}\n'
    )
    if conversation_category and conversation_category.initial_prompt:
        instructions += (
            f'Additional instructions before starting:\n{conversation_category.initial_prompt}\n'
        )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.openai.com/v1/realtime/sessions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': MODEL,
                'voice': 'echo',
                'input_audio_transcription': {'language': 'en', 'model': 'gpt-4o-transcribe'},
                'instructions': instructions,
                'turn_detection': {
                    'type': 'server_vad',
                    'threshold': 0.8,
                    'prefix_padding_ms': 300,
                    'silence_duration_ms': 500,
                },
                'speed': 0.9,
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=str(e)) from e

        data = response.json()
        data['persona_name'] = conversation_scenario.persona_name
        data['category_name'] = conversation_category_name

        return data
