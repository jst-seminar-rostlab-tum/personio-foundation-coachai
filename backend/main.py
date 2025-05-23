from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import messages_route, twilio_route, users_route

app = FastAPI(title='CoachAI', debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(messages_route.router)
app.include_router(users_route.router)
app.include_router(twilio_route.router)


@app.get('/')
async def root() -> dict:
    return {'message': 'Welcome to the API'}
