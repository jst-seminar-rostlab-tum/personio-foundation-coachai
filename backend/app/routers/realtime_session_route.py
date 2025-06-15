import os

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='', tags=['realtime-session'])


@router.get('/realtime-session')
async def get_realtime_session() -> dict:
    """
    Proxies a POST request to OpenAI's realtime sessions endpoint
    and returns the JSON response.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY not set')

    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.openai.com/v1/realtime/sessions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o-realtime-preview-2025-06-03',
                'voice': 'verse',
                'input_audio_transcription': {'language': 'en', 'model': 'gpt-4o-mini-transcribe'},
                'instructions': 'Speak only in English.',
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
