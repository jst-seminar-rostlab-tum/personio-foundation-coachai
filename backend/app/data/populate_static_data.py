import json
import os
from datetime import UTC, datetime

from data.dummy_data import get_dummy_user_data
from database import get_supabase_client
from sqlmodel import Session as DBSession
from sqlmodel import delete, select

from app.data import (
    get_dummy_app_configs,
)
from app.database import engine
from app.enums.language import LanguageCode
from app.models import AppConfig, ConversationCategory, UserProfile

base_dir = os.path.dirname(__file__)
with open(os.path.join(base_dir, 'initial_prompts.json'), encoding='utf-8') as f:
    initial_prompt_data = json.load(f)

STATIC_CATEGORIES = [
    ConversationCategory(
        id='giving_feedback',
        name='Giving Feedback',
        initial_prompt=initial_prompt_data['giving_feedback'],
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
    ConversationCategory(
        id='performance_reviews',
        name='Performance Reviews',
        initial_prompt=initial_prompt_data['performance_reviews'],
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
    ConversationCategory(
        id='conflict_resolution',
        name='Conflict Resolution',
        initial_prompt=initial_prompt_data['conflict_resolution'],
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
    ConversationCategory(
        id='salary_discussions',
        name='Salary Discussions',
        initial_prompt=initial_prompt_data['salary_discussions'],
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
]

# Placeholder for static personas
STATIC_PERSONAS = []


def populate_demo_users() -> None:
    dummy_users = get_dummy_user_data()
    supabase = get_supabase_client()

    with DBSession(engine) as db_session:
        db_session.exec(delete(UserProfile))
        db_session.commit()

    for user in supabase.auth.admin.list_users():
        supabase.auth.admin.delete_user(user.id)

    for user in dummy_users:
        supabase.auth.admin.create_user(user.supabase_profile)

        with DBSession(engine) as db_session:
            db_session.add(user.user_profile)
            db_session.commit()


def populate_static_categories() -> None:
    """
    Populate the database with static categories.
    """
    with DBSession(engine) as session:
        for cat in STATIC_CATEGORIES:
            existing = session.exec(
                select(ConversationCategory).where(ConversationCategory.name == cat.name)
            ).first()
            if not existing:
                session.add(cat)
        session.commit()


def populate_app_config() -> None:
    """
    Populate the database with app configs.
    """
    print('Populating app configs...')
    with DBSession(engine) as session:
        app_configs = get_dummy_app_configs()
        for config in app_configs:
            existing = session.exec(select(AppConfig).where(AppConfig.key == config.key)).first()
            if not existing:
                session.add(config)
        session.commit()


if __name__ == '__main__':
    populate_static_categories()
    populate_app_config()
    populate_demo_users()
