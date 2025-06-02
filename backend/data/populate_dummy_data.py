import os

from sqlalchemy import text
from sqlmodel import Session, SQLModel

from backend.data import (
    get_dummy_confidence_areas,
    get_dummy_conversation_categories,
    get_dummy_conversation_turns,
    get_dummy_difficulty_levels,
    get_dummy_experiences,
    get_dummy_goals,
    get_dummy_languages,
    get_dummy_learning_styles,
    get_dummy_ratings,
    get_dummy_roles,
    get_dummy_session_lengths,
    get_dummy_training_cases,
    get_dummy_training_preparations,
    get_dummy_training_session_feedback,
    get_dummy_training_sessions,
    get_dummy_user_confidence_scores,
    get_dummy_user_goals,
    get_dummy_user_profiles,
)
from backend.database import engine
from backend.models.hr_information import HrInformation


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
        # Populate Learning Styles
        learning_styles = get_dummy_learning_styles()
        session.add_all(learning_styles)

        # Populate Session Lengths
        session_lengths = get_dummy_session_lengths()
        session.add_all(session_lengths)

        # Commit all to get IDs
        session.commit()

        # Populate User Profiles
        user_profiles = get_dummy_user_profiles(
            roles, experiences, learning_styles, session_lengths
        )
        session.add_all(user_profiles)

        # Commit to get UserProfile IDs
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
        ratings = get_dummy_ratings(training_sessions, training_cases)
        session.add_all(ratings)

        # Commit all the above
        session.commit()

        # Populate Confidence Areas
        confidence_areas = get_dummy_confidence_areas()
        session.add_all(confidence_areas)
        session.commit()

        # Populate User Confidence Scores
        user_confidence_scores = get_dummy_user_confidence_scores(user_profiles, confidence_areas)
        session.add_all(user_confidence_scores)
        session.commit()

        print('Dummy data populated successfully!')

        # Vector store setup for RAG
        print('Creating empty vector store')
        empty_vector_data = HrInformation(content='', meta_data={}, embedding=[0.0] * 768)
        session.add(empty_vector_data)
        session.commit()
        print('Vector store created successfully!')

        print('Granting anon access to hr_information...')
        permissions_sql_path = os.path.join(os.path.dirname(__file__), 'permissions.sql')
        with open(permissions_sql_path) as f:
            session.exec(text(f.read()))
        session.commit()
        print('Permissions granted.')

        print('Saving match_function for RAG')
        sql_path = os.path.join(os.path.dirname(__file__), '..', 'rag', 'match_function.sql')
        with open(sql_path) as f:
            session.exec(text(f.read()))
            session.commit()
        print('Saved match_function.sql')


if __name__ == '__main__':
    populate_data()
