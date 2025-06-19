import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables
from app.routers import (
    admin_dashboard_stats_route,
    app_config_route,
    auth_route,
    conversation_category_route,
    conversation_scenario_route,
    rating_route,
    realtime_session_route,
    review_route,
    session_route,
    session_turn_route,
    user_confidence_score_route,
    user_goals_route,
    user_profile_route,
    user_profile_stats_route,
)

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(message)s',
)

app = FastAPI(title='CoachAI', debug=settings.stage == 'dev')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_route.router)
app.include_router(conversation_category_route.router)
app.include_router(conversation_scenario_route.router)
app.include_router(session_route.router)
app.include_router(session_turn_route.router)
app.include_router(rating_route.router)
app.include_router(user_profile_route.router)
app.include_router(user_profile_stats_route.router)
app.include_router(user_goals_route.router)
app.include_router(user_confidence_score_route.router)
app.include_router(app_config_route.router)
app.include_router(admin_dashboard_stats_route.router)
app.include_router(review_route.router)
app.include_router(realtime_session_route.router)


# Create database tables on startup
@app.on_event('startup')
def on_startup() -> None:
    create_db_and_tables()


# app.include_router(twilio_route.router)


@app.get('')
async def root() -> dict:
    return {'message': 'Welcome to the API'}
