import json
import os
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.data import create_mock_users, delete_mock_users, get_dummy_user_profiles
from app.database import engine
from app.models import ConversationCategory, UserProfile
from app.models.language import LanguageCode

base_dir = os.path.dirname(__file__)
with open(os.path.join(base_dir, 'initial_prompts.json'), encoding='utf-8') as f:
    initial_prompt_data = json.load(f)
with open(os.path.join(base_dir, 'default_contexts.json'), encoding='utf-8') as f:
    default_context_data = json.load(f)


STATIC_CATEGORIES = [
    ConversationCategory(
        id='11111111-1111-1111-1111-111111111111',
        name='Giving Feedback',
        system_prompt='You are an expert in providing constructive feedback.',
        initial_prompt=initial_prompt_data['giving_feedback'],
        ai_setup={'type': 'feedback', 'complexity': 'medium'},
        default_context=default_context_data['giving_feedback'],
        default_goal='Provide constructive feedback effectively.',
        default_other_party='Team member',
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
    ConversationCategory(
        id='22222222-2222-2222-2222-222222222222',
        name='Performance Reviews',
        system_prompt='You are a manager conducting performance reviews.',
        initial_prompt=initial_prompt_data['performance_reviews'],
        ai_setup={'type': 'review', 'complexity': 'high'},
        default_context=default_context_data['performance_reviews'],
        default_goal='Evaluate and discuss employee performance.',
        default_other_party='Employee',
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
    ConversationCategory(
        id='33333333-3333-3333-3333-333333333333',
        name='Conflict Resolution',
        system_prompt='You are a mediator resolving conflicts.',
        initial_prompt=initial_prompt_data['conflict_resolution'],
        ai_setup={'type': 'mediation', 'complexity': 'high'},
        default_context=default_context_data['conflict_resolution'],
        default_goal='Resolve conflicts and improve team dynamics.',
        default_other_party='Team members',
        is_custom=False,
        language_code=LanguageCode.en,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    ),
    ConversationCategory(
        id='44444444-4444-4444-4444-444444444444',
        name='Salary Discussions',
        system_prompt='You are a negotiator discussing salary expectations.',
        initial_prompt=initial_prompt_data['salary_discussions'],
        ai_setup={'type': 'negotiation', 'complexity': 'medium'},
        default_context=default_context_data['salary_discussions'],
        default_goal='Reach a mutually beneficial agreement on salary.',
        default_other_party='Employer',
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
        statement = select(UserProfile).where(UserProfile.id.in_(user_profile_ids))
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
            stmt = (
                insert(ConversationCategory)
                .values(**cat.model_dump())
                .on_conflict_do_nothing(index_elements=['name'])
            )
            session.execute(stmt)
        session.commit()


def populate_static_personas() -> None:
    """
    Populate the database with static personas.
    """
    # with DBSession(engine) as session:
    #     for persona in STATIC_PERSONAS:
    #         stmt = insert(Persona).values(**persona.model_dump())
    #           .on_conflict_do_nothing(index_elements=['id'])
    #         session.execute(stmt)
    #     session.commit()
    pass


if __name__ == '__main__':
    populate_demo_users()
    populate_static_categories()
    populate_static_personas()
