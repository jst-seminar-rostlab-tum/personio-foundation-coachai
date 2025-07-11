import json
import os
from datetime import UTC, datetime

from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.data import create_mock_users, delete_mock_users, get_dummy_user_profiles
from app.database import engine
from app.enums.language import LanguageCode
from app.models import ConversationCategory, UserProfile

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
    """
    Populate the database with demo users.
    """
    print('Removing mock users...')
    delete_mock_users()

    print('Creating mock users...')
    create_mock_users()

    with DBSession(engine) as db_session:
        user_profiles = get_dummy_user_profiles()

        user_profile_ids = [profile.id for profile in user_profiles]
        statement = select(UserProfile).where(col(UserProfile.id).in_(user_profile_ids))
        results = db_session.exec(statement).all()
        for profile in results:
            db_session.delete(profile)
        db_session.commit()

        # Populate User Profiles
        print('Creating user profiles')
        db_session.add_all(user_profiles)
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


def populate_static_personas() -> None:
    """
    Populate the database with static personas.
    """
    pass


if __name__ == '__main__':
    populate_demo_users()
    populate_static_categories()
    populate_static_personas()
