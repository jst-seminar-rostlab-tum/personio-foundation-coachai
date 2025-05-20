import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

"""
The Session object controls the parameters of the interaction, like 
- the model being used, 
- the voice used to generate output, 
- the system instructions for the model,
and other configuration.

Run the FastAPI app:
1. Navigate to the backend folder
2. Run:
    uvicorn core.sts_model.openai.session_route:app --reload --port <PORT_NUMBER>
Replace <PORT_NUMBER> with your desired port, e.g., 7000:
    uvicorn core.sts_model.openai.session_route:app --reload --port 7000
"""

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_SESSION_URL = 'https://api.openai.com/v1/realtime/sessions'
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o-mini-realtime-preview-2024-12-17')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # oder ["*"] für alle
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

"""
Gets an ephemeral session token from OpenAI's Realtime API.
This token is used to authenticate the WebRTC session and can only be used once.
The session token is valid for a short period of time and should be used immediately.
"""


@app.get('/session')
async def get_session() -> JSONResponse:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail='OPENAI_API_KEY is not set')

    payload = {
        'model': MODEL_NAME,
        'voice': 'verse',
        'instructions': 'You are a employee and you are talking to your manager. '
        + 'You are a bad employee so the manager is angry at you. '
        + "You are trying to convince the manager that you're a good employee"
        + "and he shouldn't fire you.",  # TODO: different instructions per training case
        'input_audio_transcription': {'model': 'whisper-1'},
        'max_response_output_tokens': 2000,
    }

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENAI_SESSION_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(content=response.json())
