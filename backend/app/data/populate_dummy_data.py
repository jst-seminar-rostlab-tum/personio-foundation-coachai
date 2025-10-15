from pathlib import Path

from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, text

from app.data import (
    get_dummy_admin_stats,
    get_dummy_app_configs,
    get_dummy_conversation_categories,
    get_dummy_conversation_scenarios,
    get_dummy_live_feedback_data,
    get_dummy_reviews,
    get_dummy_scenario_preparations,
    get_dummy_session_feedback,
    get_dummy_session_turns,
    get_dummy_sessions,
    get_dummy_user_confidence_scores,
    get_dummy_user_goals,
)
from app.data.dummy_data import get_dummy_user_data
from app.database import engine
from app.models.hr_information import HrInformation


def populate_data() -> None:
    with DBSession(engine) as db_session:
        db_session.exec(text('CREATE EXTENSION IF NOT EXISTS vector'))  # type: ignore
        db_session.commit()

        print('Dropping tables...')
        SQLModel.metadata.drop_all(engine)

        # print('Removing mock users...')
        # delete_mock_users()

        print('Creating tables...')
        SQLModel.metadata.create_all(engine)

        # to get their IDs
        db_session.commit()

        # Populate User Profiles
        user_profiles = [wrapper.user_profile for wrapper in get_dummy_user_data()]
        db_session.add_all(user_profiles)

        # Commit user profiles to get their IDs
        db_session.commit()

        # Populate User Goals
        user_goals = get_dummy_user_goals(user_profiles)
        db_session.add_all(user_goals)

        # Populate Conversation Categories
        conversation_categories = get_dummy_conversation_categories()
        db_session.add_all(conversation_categories)

        # Populate Conversation Scenarios
        conversation_scenarios = get_dummy_conversation_scenarios(
            user_profiles, conversation_categories
        )
        db_session.add_all(conversation_scenarios)
        db_session.commit()

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

        # Populate Admin Dashboard Stats
        admin_stats = get_dummy_admin_stats()
        db_session.add_all(admin_stats)

        # Add app configs
        app_configs = get_dummy_app_configs()
        db_session.add_all(app_configs)

        # Populate Reviews
        reviews = get_dummy_reviews(user_profiles, sessions)
        db_session.add_all(reviews)

        # Commit all data
        db_session.commit()

        # Populate User Confidence Scores
        user_confidence_scores = get_dummy_user_confidence_scores(user_profiles)
        db_session.add_all(user_confidence_scores)

        # Populate live feedback
        live_feedback = get_dummy_live_feedback_data(session_turns)
        db_session.add_all(live_feedback)

        # Commit all data
        db_session.commit()
        print('Dummy data populated successfully!')

        print('Creating empty vector store')
        empty_vector_data = HrInformation(content='', meta_data={}, embedding=[0.0] * 768)
        db_session.add(empty_vector_data)
        db_session.commit()
        path_match_documents = Path(__file__).resolve().parent.parent / 'rag' / 'match_function.sql'
        sql_query_match_documents = path_match_documents.read_text(encoding='utf-8')
        db_session.execute(text(sql_query_match_documents))
        db_session.commit()
        print('Vector store created successfully!')
        # print('Creating mock users...')
        # create_mock_users()


if __name__ == '__main__':
    populate_data()
