import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import NoReturn

import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.database import get_db_session
from app.routers import (
    admin_dashboard_stats_route,
    app_config_route,
    auth_route,
    conversation_category_route,
    conversation_scenario_route,
    live_feedback_route,
    realtime_session_route,
    review_route,
    session_turn_route,
    sessions_route,
    signed_urls_route,
    user_profile_route,
)
from app.services.data_retention_service import cleanup_old_session_turns

if settings.stage == 'dev' and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            HttpxIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=0.1,
        enable_tracing=True,
    )

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    stream=sys.stdout,
    format='%(message)s',
)
logging.info(f'DEFAULT_MODEL: {settings.DEFAULT_MODEL}')

scheduler = BackgroundScheduler()


def scheduled_cleanup() -> None:
    db_gen = get_db_session()
    db = next(db_gen)
    try:
        cleanup_old_session_turns(db)
    finally:
        db_gen.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    scheduler.add_job(scheduled_cleanup, 'cron', hour=3, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title='CoachAI', debug=settings.stage == 'dev', lifespan=lifespan)


class TimezoneAwareMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        timezone = request.headers.get('x-timezone')

        request.state.timezone = timezone if timezone else 'UTC'
        return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(TimezoneAwareMiddleware)

app.include_router(auth_route.router)
app.include_router(conversation_category_route.router)
app.include_router(conversation_scenario_route.router)
app.include_router(sessions_route.router)
app.include_router(session_turn_route.router)
app.include_router(user_profile_route.router)
app.include_router(app_config_route.router)
app.include_router(admin_dashboard_stats_route.router)
app.include_router(review_route.router)
app.include_router(realtime_session_route.router)
app.include_router(signed_urls_route.router)
app.include_router(live_feedback_route.router)


@app.get('/test-error')
def trigger_error() -> NoReturn:
    raise Exception('Test error from FastAPI backend')
