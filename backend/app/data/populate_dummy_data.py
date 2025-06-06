from sqlmodel import Session, SQLModel, text

from app.data import (
    get_dummy_admin_stats,
    get_dummy_app_configs,
    get_dummy_confidence_areas,
    get_dummy_conversation_categories,
    get_dummy_conversation_turns,
    get_dummy_difficulty_levels,
    get_dummy_experiences,
    get_dummy_goals,
    get_dummy_languages,
    get_dummy_learning_styles,
    get_dummy_ratings,
    get_dummy_session_lengths,
    get_dummy_training_cases,
    get_dummy_training_preparations,
    get_dummy_training_session_feedback,
    get_dummy_training_sessions,
    get_dummy_user_confidence_scores,
    get_dummy_user_feedbacks,
    get_dummy_user_goals,
    get_dummy_user_profiles,
)
from app.database import engine
from app.models.hr_information import HrInformation


def populate_data() -> None:
    with Session(engine) as session:
        session.exec(text('CREATE EXTENSION IF NOT EXISTS vector'))  # type: ignore
        session.commit()

        print('Dropping tables...')
        SQLModel.metadata.drop_all(engine)

        print('Creating tables...')
        SQLModel.metadata.create_all(engine)

        # Populate Languages
        languages = get_dummy_languages()
        session.add_all(languages)
        session.commit()

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

        # Commit roles, experiences, goals, learning_styles, session_length and difficulty levels
        # to get their IDs
        session.commit()

        # Populate User Profiles
        user_profiles = get_dummy_user_profiles(experiences, learning_styles, session_lengths)
        session.add_all(user_profiles)

        # Commit user profiles to get their IDs
        session.commit()

        # Populate User Goals
        user_goals = get_dummy_user_goals(user_profiles, goals)
        session.add_all(user_goals)

        # Populate User Feedbacks
        user_feedbacks = get_dummy_user_feedbacks(user_profiles)
        session.add_all(user_feedbacks)

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

        # Populate Admin Dashboard Stats
        admin_stats = get_dummy_admin_stats()
        session.add_all(admin_stats)

        # Commit all data
        session.commit()
        # Populate Confidence Areas
        confidence_areas = get_dummy_confidence_areas()
        session.add_all(confidence_areas)
        session.commit()
        # Populate User Confidence Scores
        user_confidence_scores = get_dummy_user_confidence_scores(user_profiles, confidence_areas)
        session.add_all(user_confidence_scores)

        app_configs = get_dummy_app_configs()
        session.add_all(app_configs)
        # Commit all data
        session.commit()
        print('Dummy data populated successfully!')

        print('Creating empty vector store')
        empty_vector_data = HrInformation(content='', meta_data={}, embedding=[0.0] * 768)
        session.add(empty_vector_data)
        session.commit()
        print('Vector store created successfully!')


if __name__ == '__main__':
    populate_data()
