import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables, get_db_session
from app.routers import (
    admin_dashboard_stats_route,
    app_config_route,
    auth_route,
    conversation_category_route,
    conversation_scenario_route,
    live_feedback_route,
    realtime_session_route,
    review_route,
    session_route,
    session_turn_route,
    signed_url_route,
    user_profile_route,
)
from app.services.data_retention_service import cleanup_old_session_turns

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    stream=sys.stdout,
    format='%(message)s',
)

scheduler = BackgroundScheduler()


def scheduled_cleanup() -> None:
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        cleanup_old_session_turns(db)
    finally:
        db_gen.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    scheduler.add_job(scheduled_cleanup, 'cron', hour=3, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title='CoachAI', debug=settings.stage == 'dev', lifespan=lifespan)

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
app.include_router(user_profile_route.router)
app.include_router(app_config_route.router)
app.include_router(admin_dashboard_stats_route.router)
app.include_router(review_route.router)
app.include_router(realtime_session_route.router)
app.include_router(signed_url_route.router)
app.include_router(live_feedback_route.router)
