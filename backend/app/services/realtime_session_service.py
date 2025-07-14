import json
import os
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.config import settings
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.session import Session, SessionStatus
from app.models.user_profile import UserProfile

if settings.FORCE_CHEAP_MODEL:
    MODEL = 'gpt-4o-mini-realtime-preview-2024-12-17'
else:
    MODEL = 'gpt-4o-realtime-preview-2025-06-03'


class RealtimeSessionService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def _get_voice(self, persona_name: str) -> str:
        """
        Returns the voice to be used based on the persona name.
        """
        persona_name = persona_name.lower()
        if 'angry' in persona_name:
            return 'verse'
        elif 'positive' in persona_name:
            return 'shimmer'
        elif 'casual' in persona_name:
            return 'alloy'
        elif 'shy' in persona_name:
            return 'sage'
        elif 'sad' in persona_name:
            return 'ash'
        else:
            return 'echo'

    def get_persona_difficulty_modifier(self, persona_name: str, difficulty: str) -> str | None:
        """
        Returns the modifier string for a given persona name and difficulty.
        """
        modifiers_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'persona_difficulty_modifiers.json'
        )

        print(f'Loading persona difficulty modifiers from {modifiers_path}')
        try:
            with open(modifiers_path) as f:
                modifiers = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        personas = modifiers.get('personas', {})
        persona_data = personas.get(persona_name)
        if not persona_data:
            return None

        difficulties = persona_data.get('difficulties', {})
        difficulty_data = difficulties.get(difficulty)
        if not difficulty_data:
            return None

        # Format the difficulty data as a nicely formatted string
        formatted = []
        for key, value in difficulty_data.items():
            if isinstance(value, list):
                formatted.append(
                    f'{key.replace("_", " ").title()}:\n' + '\n'.join(f'- {item}' for item in value)
                )
            else:
                formatted.append(f'{key.replace("_", " ").title()}:\n{value}')
        return '\n\n'.join(formatted)

    async def get_realtime_session(self, session_id: UUID, user_profile: UserProfile) -> dict:
        """
        Proxies a POST request to OpenAI's realtime sessions endpoint
        and returns the JSON response.
        """
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='OPENAI_API_KEY not set'
            )

        session = self.db.exec(select(Session).where(Session.id == session_id)).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')
        if session.status is SessionStatus.completed:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, detail='Session is already completed'
            )

        conversation_scenario = self.db.exec(
            select(ConversationScenario).where(ConversationScenario.id == session.scenario_id)
        ).first()
        if not conversation_scenario:
            raise HTTPException(
                status_code=404, detail='No conversation scenario found for this session'
            )

        conversation_category = None
        if conversation_scenario.category_id:
            conversation_category = self.db.exec(
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
            conversation_category_name = conversation_category.id
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

        persona_difficulty_modifier = self.get_persona_difficulty_modifier(
            conversation_scenario.persona_name, conversation_scenario.difficulty_level
        )
        if persona_difficulty_modifier:
            print(f'Using difficulty modifier for {conversation_scenario.persona_name}:')
            instructions += (
                f'\n\nThe following difficulty modifiers apply:\n'
                f'{json.dumps(persona_difficulty_modifier, indent=2)}\n'
            )

        if conversation_category and conversation_category.initial_prompt:
            instructions += (
                f'Additional instructions before starting:\n'
                f'{conversation_category.initial_prompt}\n'
            )

        ai_voice = self._get_voice(conversation_scenario.persona_name)
        language = conversation_scenario.language_code.value

        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.openai.com/v1/realtime/sessions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': MODEL,
                    'voice': ai_voice,
                    'input_audio_transcription': {
                        'language': language,
                        'model': 'gpt-4o-transcribe',
                    },
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
