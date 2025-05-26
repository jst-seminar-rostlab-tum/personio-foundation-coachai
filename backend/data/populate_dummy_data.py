from sqlmodel import Session, SQLModel

from backend.data import (
    get_dummy_conversation_categories,
    get_dummy_conversation_turns,
    get_dummy_difficulty_levels,
    get_dummy_experiences,
    get_dummy_goals,
    get_dummy_languages,
    get_dummy_ratings,
    get_dummy_roles,
    get_dummy_training_cases,
    get_dummy_training_preparations,
    get_dummy_training_session_feedback,
    get_dummy_training_sessions,
    get_dummy_user_goals,
    get_dummy_user_profiles,
)
from backend.database import engine


def populate_data() -> None:
    print('Dropping tables...')
    SQLModel.metadata.drop_all(engine)

    print('Creating tables...')
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Populate Languages
        languages = get_dummy_languages()
        session.add_all(languages)
        session.commit()
        # Populate Roles
        roles = get_dummy_roles()
        session.add_all(roles)

        # Populate Experiences
        experiences = get_dummy_experiences()
        session.add_all(experiences)

        # Populate Goals
        goals = get_dummy_goals()
        session.add_all(goals)

        # Populate Difficulty Levels
        difficulty_levels = get_dummy_difficulty_levels()
        session.add_all(difficulty_levels)

        # Commit roles, experiences, goals, and difficulty levels to get their IDs
        session.commit()

        # Populate User Profiles
        user_profiles = get_dummy_user_profiles(roles, experiences)
        session.add_all(user_profiles)

        # Commit user profiles to get their IDs
        session.commit()

        # Populate User Goals
        user_goals = get_dummy_user_goals(user_profiles, goals)
        session.add_all(user_goals)

        # Populate Training Cases
        training_cases = get_dummy_training_cases(user_profiles, difficulty_levels)
        session.add_all(training_cases)
        session.commit()

        # Populate Conversation Categories
        conversation_categories = get_dummy_conversation_categories()
        session.add_all(conversation_categories)

        # Populate Training Sessions
        training_sessions = get_dummy_training_sessions(training_cases)
        session.add_all(training_sessions)

        # Commit training sessions to get their IDs
        session.commit()

        # Populate Conversation Turns
        conversation_turns = get_dummy_conversation_turns(training_sessions)
        session.add_all(conversation_turns)

        # Populate Training Session Feedback
        training_session_feedback = get_dummy_training_session_feedback(training_sessions)
        session.add_all(training_session_feedback)

        # Populate Training Preparations
        training_preparations = get_dummy_training_preparations(training_cases)
        session.add_all(training_preparations)

        # Populate Ratings
        ratings = get_dummy_ratings(
            training_sessions, training_cases
        )  # Pass both sessions and cases
        session.add_all(ratings)

        # Commit all data
        session.commit()

        print('Dummy data populated successfully!')


if __name__ == '__main__':
    populate_data()
