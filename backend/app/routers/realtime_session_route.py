from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.config import settings
from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.session import Session
from app.models.user_profile import UserProfile

router = APIRouter(prefix='', tags=['realtime-session'])

if settings.FORCE_CHEAP_MODEL:
    MODEL = 'gpt-4o-mini-realtime-preview-2024-12-17'
else:
    MODEL = 'gpt-4o-realtime-preview-2025-06-03'


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
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY not set')

    session = db_session.exec(select(Session).where(Session.id == session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    conversation_scenario = db_session.exec(
        select(ConversationScenario).where(ConversationScenario.id == session.scenario_id)
    ).first()
    if not conversation_scenario:
        raise HTTPException(
            status_code=404, detail='No conversation scenario found for this session'
        )
    conversation_category = db_session.exec(
        select(ConversationCategory).where(
            ConversationCategory.id == conversation_scenario.category_id
        )
    ).first()
    if not conversation_category:
        raise HTTPException(
            status_code=404, detail='No conversation category found for this scenario'
        )

    instructions = ''

    if conversation_scenario:
        instructions += conversation_scenario.context

    if conversation_category:
        instructions += '\n\n' + conversation_category.initial_prompt

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

        return response.json()
