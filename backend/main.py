from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

# from .database import engine
from .database import create_db_and_tables
from .routers import (
    conversation_category_route,
    conversation_turn_route,
    language_route,
    rating_route,
    scenario_template_route,
    training_case_route,
    training_preparation_route,
    training_session_feedback_route,
    training_session_route,
    user_profile_route,
)

# models.Base.metadata.create_all(bind=engine)

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
app.include_router(scenario_template_route.router)
app.include_router(conversation_turn_route.router)
app.include_router(training_session_feedback_route.router)
app.include_router(rating_route.router)
app.include_router(user_profile_route.router)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()