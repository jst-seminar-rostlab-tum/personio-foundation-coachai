from sqlmodel import Session as DBSession
from sqlmodel import select

from app.data import create_mock_users, delete_mock_users, get_dummy_user_profiles
from app.database import engine
from app.models import UserProfile


def populate_demo_users() -> None:
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


if __name__ == '__main__':
    populate_demo_users()
