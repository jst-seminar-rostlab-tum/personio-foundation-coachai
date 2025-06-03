from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

# from .database import engine
from .database import create_db_and_tables
from .routers import (
    app_config_route,
    confidence_area_route,
    conversation_category_route,
    conversation_turn_route,
    goal_route,
    language_route,
    learning_style_route,
    personalization_options_route,
    rating_route,
    session_length_route,
    training_case_route,
    training_preparation_route,
    training_session_feedback_route,
    training_session_route,
    user_confidence_score_route,
    user_goals_route,
    user_profile_route,
)

app = FastAPI(title='CoachAI', debug=settings.stage == 'dev')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(language_route.router)
app.include_router(conversation_category_route.router)
app.include_router(training_case_route.router)
app.include_router(training_session_route.router)
app.include_router(training_preparation_route.router)
app.include_router(conversation_turn_route.router)
app.include_router(training_session_feedback_route.router)
app.include_router(rating_route.router)
app.include_router(user_profile_route.router)
app.include_router(user_goals_route.router)
app.include_router(goal_route.router)
app.include_router(confidence_area_route.router)
app.include_router(user_confidence_score_route.router)
app.include_router(learning_style_route.router)
app.include_router(session_length_route.router)
app.include_router(personalization_options_route.router)
app.include_router(app_config_route.router)


# Create database tables on startup
@app.on_event('startup')
def on_startup() -> None:
    create_db_and_tables()


# app.include_router(twilio_route.router)


@app.get('/')
async def root() -> dict:
    return {'message': 'Welcome to the API'}
