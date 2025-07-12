from sqlmodel import Session as DBSession
from sqlmodel import select

from app.models.app_config import AppConfig
from app.models.conversation_scenario import ConversationScenario
from app.models.review import Review
from app.models.user_confidence_score import UserConfidenceScore
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.schemas.user_export import (
    ExportConfidenceScore,
    ExportConversationScenario,
    ExportReview,
    ExportScenarioPreparation,
    ExportSession,
    ExportSessionFeedback,
    ExportSessionTurn,
    ExportUserGoal,
    ExportUserProfile,
    UserDataExport,
)


def _build_export_user_profile(
    user_profile: UserProfile, db_session: DBSession
) -> ExportUserProfile:
    """Build export user profile from UserProfile model."""
    try:
        daily_session_limit = db_session.exec(
            select(AppConfig.value).where(AppConfig.key == 'dailyUserSessionLimit')
        ).first()
        daily_session_limit = int(daily_session_limit) if daily_session_limit is not None else 0

        # If session limit is not configured, assume limit is hit (safety feature)
        if daily_session_limit == 0:
            num_remaining_daily_sessions = 0
        else:
            num_remaining_daily_sessions = max(
                0, daily_session_limit - user_profile.sessions_created_today
            )
        return ExportUserProfile(
            user_id=str(user_profile.id),
            full_name=user_profile.full_name,
            email=user_profile.email,
            phone_number=user_profile.phone_number,
            preferred_language_code=str(user_profile.preferred_language_code),
            account_role=str(user_profile.account_role),
            professional_role=str(user_profile.professional_role),
            experience=str(user_profile.experience),
            preferred_learning_style=str(user_profile.preferred_learning_style),
            updated_at=user_profile.updated_at.isoformat() if user_profile.updated_at else None,
            store_conversations=user_profile.store_conversations,
            total_sessions=user_profile.total_sessions,
            training_time=user_profile.training_time,
            current_streak_days=user_profile.current_streak_days,
            score_sum=user_profile.score_sum,
            goals_achieved=user_profile.goals_achieved,
            num_remaining_daily_sessions=num_remaining_daily_sessions,
        )
    except Exception as e:
        # Add debugging information
        print(f'Error building export user profile: {e}')
        print('User profile data types:')
        print(f'  training_time: {type(user_profile.training_time)} = {user_profile.training_time}')
        print(f'  score_sum: {type(user_profile.score_sum)} = {user_profile.score_sum}')
        print(
            f'  total_sessions: {type(user_profile.total_sessions)} = {user_profile.total_sessions}'
        )
        raise


def _build_export_goals(goals: list[UserGoal]) -> list[ExportUserGoal]:
    """Build export goals from UserGoal models."""
    return [
        ExportUserGoal(
            goal=str(goal.goal),
            updated_at=goal.updated_at.isoformat() if goal.updated_at else None,
        )
        for goal in goals
    ]


def _build_export_confidence_scores(
    confidence_scores: list[UserConfidenceScore],
) -> list[ExportConfidenceScore]:
    """Build export confidence scores from UserConfidenceScore models."""
    return [
        ExportConfidenceScore(
            confidence_area=str(cs.confidence_area),
            score=cs.score,
            updated_at=cs.updated_at.isoformat() if cs.updated_at else None,
        )
        for cs in confidence_scores
    ]


def _build_export_scenarios(
    scenarios: list[ConversationScenario],
) -> list[ExportConversationScenario]:
    """Build export scenarios from ConversationScenario models."""
    try:
        return [
            ExportConversationScenario(
                id=str(s.id),
                category_id=s.category_id,
                custom_category_label=s.custom_category_label,
                language_code=str(s.language_code),
                persona=s.persona,
                situational_facts=s.situational_facts,
                difficulty_level=str(s.difficulty_level),
                status=str(s.status),
                created_at=s.created_at.isoformat() if s.created_at else None,
                updated_at=s.updated_at.isoformat() if s.updated_at else None,
            )
            for s in scenarios
        ]
    except Exception as e:
        # Add debugging information
        print(f'Error building export scenarios: {e}')
        if scenarios:
            s = scenarios[0]  # Use first scenario for debugging
            print('Sample scenario data types:')
            print(f'  category_id: {type(s.category_id)} = {s.category_id}')
            print(f'  language_code: {type(s.language_code)} = {s.language_code}')
            print(f'  difficulty_level: {type(s.difficulty_level)} = {s.difficulty_level}')
            print(f'  status: {type(s.status)} = {s.status}')
        raise


def _build_export_scenario_preparations(
    scenarios: list[ConversationScenario],
) -> list[ExportScenarioPreparation]:
    """Build export scenario preparations from ConversationScenario models."""
    try:
        scenario_preparations = []
        for s in scenarios:
            if hasattr(s, 'preparation') and s.preparation:
                prep = s.preparation
                scenario_preparations.append(
                    ExportScenarioPreparation(
                        id=str(prep.id),
                        scenario_id=str(prep.scenario_id),
                        objectives=prep.objectives,
                        key_concepts=prep.key_concepts,
                        prep_checklist=prep.prep_checklist,
                        status=str(prep.status),
                        created_at=prep.created_at.isoformat() if prep.created_at else None,
                        updated_at=prep.updated_at.isoformat() if prep.updated_at else None,
                    )
                )
        return scenario_preparations
    except Exception as e:
        # Add debugging information
        print(f'Error building export scenario preparations: {e}')
        for s in scenarios:
            if hasattr(s, 'preparation') and s.preparation:
                prep = s.preparation
                print('Sample preparation data types:')
                print(f'  key_concepts: {type(prep.key_concepts)} = {prep.key_concepts}')
                print(f'  objectives: {type(prep.objectives)} = {prep.objectives}')
                print(f'  prep_checklist: {type(prep.prep_checklist)} = {prep.prep_checklist}')
                break
        raise


def _build_export_sessions(scenarios: list[ConversationScenario]) -> list[ExportSession]:
    """Build export sessions from ConversationScenario models."""
    try:
        sessions = []
        for scenario in scenarios:
            scenario_sessions = scenario.sessions
            for sess in scenario_sessions:
                sessions.append(sess)

        return [
            ExportSession(
                id=str(sess.id),
                scenario_id=str(sess.scenario_id),
                scheduled_at=sess.scheduled_at.isoformat() if sess.scheduled_at else None,
                started_at=sess.started_at.isoformat() if sess.started_at else None,
                ended_at=sess.ended_at.isoformat() if sess.ended_at else None,
                status=str(sess.status),
                created_at=sess.created_at.isoformat() if sess.created_at else None,
                updated_at=sess.updated_at.isoformat() if sess.updated_at else None,
            )
            for sess in sessions
        ]
    except Exception as e:
        # Add debugging information
        print(f'Error building export sessions: {e}')
        sessions = []
        for scenario in scenarios:
            scenario_sessions = scenario.sessions
            for sess in scenario_sessions:
                sessions.append(sess)

        if sessions:
            sess = sessions[0]  # Use first session for debugging
            print('Sample session data types:')
            print(f'  status: {type(sess.status)} = {sess.status}')
        raise


def _build_export_session_turns(sessions: list) -> list[ExportSessionTurn]:
    """Build export session turns from Session models."""
    session_turns = []
    for sess in sessions:
        for turn in sess.session_turns:
            session_turns.append(turn)

    return [
        ExportSessionTurn(
            id=str(turn.id),
            session_id=str(turn.session_id),
            speaker=str(turn.speaker),
            start_offset_ms=turn.start_offset_ms,
            end_offset_ms=turn.end_offset_ms,
            text=turn.text,
            audio_uri=turn.audio_uri,
            ai_emotion=turn.ai_emotion,
            created_at=turn.created_at.isoformat() if turn.created_at else None,
        )
        for turn in session_turns
    ]


def _build_export_session_feedback(sessions: list) -> list[ExportSessionFeedback]:
    """Build export session feedback from Session models."""
    session_feedbacks = []
    for sess in sessions:
        if sess.feedback:
            session_feedbacks.append(sess.feedback)

    return [
        ExportSessionFeedback(
            id=str(fb.id),
            session_id=str(fb.session_id),
            scores=fb.scores,
            tone_analysis=fb.tone_analysis,
            overall_score=fb.overall_score,
            transcript_uri=fb.transcript_uri,
            speak_time_percent=fb.speak_time_percent,
            questions_asked=fb.questions_asked,
            session_length_s=fb.session_length_s,
            goals_achieved=fb.goals_achieved,
            example_positive=fb.example_positive,
            example_negative=fb.example_negative,
            recommendations=fb.recommendations,
            status=str(fb.status),
            created_at=fb.created_at.isoformat() if fb.created_at else None,
            updated_at=fb.updated_at.isoformat() if fb.updated_at else None,
        )
        for fb in session_feedbacks
    ]


def _build_export_reviews(reviews: list[Review]) -> list[ExportReview]:
    """Build export reviews from Review models."""
    return [
        ExportReview(
            id=str(r.id),
            session_id=str(r.session_id) if r.session_id else None,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in reviews
    ]


def build_user_data_export(user_profile: UserProfile, db_session: DBSession) -> UserDataExport:
    """Build complete user data export from database models."""
    user_id = user_profile.id

    # Fetch all related data
    goals = db_session.exec(select(UserGoal).where(UserGoal.user_id == user_id)).all()
    confidence_scores = db_session.exec(
        select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
    ).all()
    scenarios = db_session.exec(
        select(ConversationScenario).where(ConversationScenario.user_id == user_id)
    ).all()
    reviews = db_session.exec(select(Review).where(Review.user_id == user_id)).all()

    # Get sessions from scenarios
    sessions = []
    for scenario in scenarios:
        scenario_sessions = scenario.sessions
        for sess in scenario_sessions:
            sessions.append(sess)

    # Build export data
    return UserDataExport(
        profile=_build_export_user_profile(user_profile, db_session),
        goals=_build_export_goals(goals),
        confidence_scores=_build_export_confidence_scores(confidence_scores),
        scenarios=_build_export_scenarios(scenarios),
        scenario_preparations=_build_export_scenario_preparations(scenarios),
        sessions=_build_export_sessions(scenarios),
        session_turns=_build_export_session_turns(sessions),
        session_feedback=_build_export_session_feedback(sessions),
        reviews=_build_export_reviews(reviews),
    )
