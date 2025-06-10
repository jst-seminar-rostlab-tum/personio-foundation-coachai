from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, text

from app.data import (
    get_dummy_admin_stats,
    get_dummy_app_configs,
    get_dummy_confidence_areas,
    get_dummy_conversation_categories,
    get_dummy_conversation_scenarios,
    get_dummy_difficulty_levels,
    get_dummy_experiences,
    get_dummy_goals,
    get_dummy_languages,
    get_dummy_learning_styles,
    get_dummy_ratings,
    get_dummy_reviews,
    get_dummy_scenario_preparations,
    get_dummy_session_feedback,
    get_dummy_session_turns,
    get_dummy_sessions,
    get_dummy_user_confidence_scores,
    get_dummy_user_goals,
    get_dummy_user_profiles,
)
from app.database import engine
from app.models.hr_information import HrInformation


def populate_data() -> None:
    with DBSession(engine) as db_session:
        db_session.exec(text('CREATE EXTENSION IF NOT EXISTS vector'))  # type: ignore
        db_session.commit()

        print('Dropping tables...')
        SQLModel.metadata.drop_all(engine)

        print('Creating tables...')
        SQLModel.metadata.create_all(engine)

        # Populate Languages
        languages = get_dummy_languages()
        db_session.add_all(languages)
        db_session.commit()

        # Populate Experiences
        experiences = get_dummy_experiences()
        db_session.add_all(experiences)

        # Populate Goals
        goals = get_dummy_goals()
        db_session.add_all(goals)

        # Populate Difficulty Levels
        difficulty_levels = get_dummy_difficulty_levels()
        db_session.add_all(difficulty_levels)
        # Populate Learning Styles
        learning_styles = get_dummy_learning_styles()
        db_session.add_all(learning_styles)

        # Commit roles, experiences, goals, learning_styles and difficulty levels
        # to get their IDs
        db_session.commit()

        # Populate User Profiles
        user_profiles = get_dummy_user_profiles(experiences, learning_styles)
        db_session.add_all(user_profiles)

        # Commit user profiles to get their IDs
        db_session.commit()

        # Populate User Goals
        user_goals = get_dummy_user_goals(user_profiles, goals)
        db_session.add_all(user_goals)

        # Populate Conversation Scenarios
        conversation_scenarios = get_dummy_conversation_scenarios(user_profiles, difficulty_levels)
        db_session.add_all(conversation_scenarios)
        db_session.commit()

        # Populate Conversation Categories
        conversation_categories = get_dummy_conversation_categories()
        db_session.add_all(conversation_categories)

        # Populate Sessions
        sessions = get_dummy_sessions(conversation_scenarios)
        db_session.add_all(sessions)

        # Commit sessions to get their IDs
        db_session.commit()

        # Populate Conversation Turns
        session_turns = get_dummy_session_turns(sessions)
        db_session.add_all(session_turns)

        # Populate Session Feedback
        session_feedback = get_dummy_session_feedback(sessions)
        db_session.add_all(session_feedback)

        # Populate Scenario Preparations
        scenario_preparations = get_dummy_scenario_preparations(conversation_scenarios)
        db_session.add_all(scenario_preparations)

        # Populate Ratings
        ratings = get_dummy_ratings(
            sessions, conversation_scenarios
        )  # Pass both sessions and scenarios
        db_session.add_all(ratings)

        # Populate Admin Dashboard Stats
        admin_stats = get_dummy_admin_stats()
        session.add_all(admin_stats)

        # Populate Reviews
        reviews = get_dummy_reviews(user_profiles, sessions)
        db_session.add_all(reviews)

        # Commit all data
        db_session.commit()
        # Populate Confidence Areas
        confidence_areas = get_dummy_confidence_areas()
        db_session.add_all(confidence_areas)
        db_session.commit()
        # Populate User Confidence Scores
        user_confidence_scores = get_dummy_user_confidence_scores(user_profiles, confidence_areas)
        db_session.add_all(user_confidence_scores)

        app_configs = get_dummy_app_configs()
        db_session.add_all(app_configs)
        # Commit all data
        db_session.commit()
        print('Dummy data populated successfully!')

        print('Creating empty vector store')
        empty_vector_data = HrInformation(content='', meta_data={}, embedding=[0.0] * 768)
        db_session.add(empty_vector_data)
        db_session.commit()
        print('Vector store created successfully!')


if __name__ == '__main__':
    populate_data()
