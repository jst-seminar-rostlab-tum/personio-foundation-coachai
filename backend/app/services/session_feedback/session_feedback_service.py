import concurrent.futures
import logging
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException
from pydantic import Field
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.camel_case import CamelModel
from app.models.session import Session
from app.models.session_feedback import FeedbackStatusEnum, SessionFeedback
from app.models.session_turn import SessionTurn
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioRead,
)
from app.schemas.session_feedback import (
    FeedbackRequest,
    GoalsAchievedCollection,
    GoalsAchievementRequest,
    NegativeExample,
    PositiveExample,
    Recommendation,
    RecommendationsCollection,
    SessionExamplesCollection,
)
from app.schemas.session_turn import SessionTurnRead
from app.services.scoring_service import ScoringService, get_scoring_service
from app.services.session_feedback.session_feedback_llm import (
    safe_generate_recommendations,
    safe_generate_training_examples,
    safe_get_achieved_goals,
)
from app.services.session_turn_service import SessionTurnService
from app.services.vector_db_context_service import query_vector_db_and_prompt


def prepare_feedback_requests(
    example_request: FeedbackRequest,
) -> tuple[GoalsAchievementRequest, FeedbackRequest]:
    """Prepare all feedback-related request objects."""
    goals_request = GoalsAchievementRequest(
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        language_code=example_request.language_code,
    )
    recommendations_request = FeedbackRequest(
        category=example_request.category,
        persona=example_request.persona,
        situational_facts=example_request.situational_facts,
        transcript=example_request.transcript,
        objectives=example_request.objectives,
        key_concepts=example_request.key_concepts,
        language_code=example_request.language_code,
    )
    return goals_request, recommendations_request


def get_hr_docs_context(
    recommendations_request: FeedbackRequest,
) -> tuple[str, list[str]]:
    """Generate HR docs context using the vector DB."""
    return query_vector_db_and_prompt(
        session_context=[
            recommendations_request.category,
            recommendations_request.persona,
            recommendations_request.situational_facts,
            recommendations_request.transcript or '',
            recommendations_request.objectives,  # type: ignore
            recommendations_request.key_concepts,
        ],
        generated_object='output',
    )


class FeedbackGenerationResult(CamelModel):
    examples_positive: list[PositiveExample] = Field(default_factory=list)
    examples_negative: list[NegativeExample] = Field(default_factory=list)
    goals: GoalsAchievedCollection = Field(
        default_factory=lambda: GoalsAchievedCollection(goals_achieved=[])
    )
    recommendations: list[Recommendation] = Field(default_factory=list)
    scores_json: dict[str, float] = Field(default_factory=dict)
    overall_score: float = 0.0
    has_error: bool = False
    full_audio_filename: str = ''
    document_names: list[str] = Field(default_factory=list)


def generate_feedback_components(
    feedback_request: FeedbackRequest,
    goals_request: GoalsAchievementRequest,
    hr_docs_context: str,
    document_names: list[str],
    conversation: ConversationScenarioRead,
    scoring_service: ScoringService,
    session_turn_service: SessionTurnService,
    session_id: UUID,
) -> FeedbackGenerationResult:
    """Run all feedback-related generation in parallel."""
    examples_positive: list[PositiveExample] = []
    examples_negative: list[NegativeExample] = []
    goals: GoalsAchievedCollection = GoalsAchievedCollection(goals_achieved=[])
    recommendations: list[Recommendation] = []
    scores_json: dict[str, float] = {}
    overall_score: float = 0.0
    has_error: bool = False
    output_blob_name: str | None = ''

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_examples = executor.submit(
            safe_generate_training_examples, feedback_request, hr_docs_context
        )
        future_goals = executor.submit(safe_get_achieved_goals, goals_request, hr_docs_context)
        future_recommendations = executor.submit(
            safe_generate_recommendations, feedback_request, hr_docs_context
        )
        future_scoring = executor.submit(scoring_service.safe_score_conversation, conversation)
        future_audio_stitch = executor.submit(
            session_turn_service.stitch_mp3s_from_gcs,
            session_id,
            f'{session_id}.mp3',
        )

        try:
            examples: SessionExamplesCollection = future_examples.result()
            examples_positive = examples.positive_examples
            examples_negative = examples.negative_examples
        except Exception as e:
            has_error = True
            logging.warning('Failed to generate examples: %s', e)

        try:
            goals = future_goals.result()
        except Exception as e:
            has_error = True
            logging.warning('Failed to generate goals: %s', e)

        try:
            recs: RecommendationsCollection = future_recommendations.result()
            recommendations = recs.recommendations
        except Exception as e:
            has_error = True
            logging.warning('Failed to generate key recommendations: %s', e)

        try:
            scoring_result = future_scoring.result()
            scores_json = {s.metric: s.score for s in scoring_result.scoring.scores}
            overall_score = scoring_result.scoring.overall_score
        except Exception as e:
            has_error = True
            logging.warning('Failed to call ScoringService: %s', e)
            scores_json = {}
            overall_score = 0.0

        try:
            output_blob_name = future_audio_stitch.result()
        except Exception as e:
            has_error = True
            logging.warning('Failed to call Audio Stitching: %s', e)

    return FeedbackGenerationResult(
        examples_positive=examples_positive,
        examples_negative=examples_negative,
        goals=goals,
        recommendations=recommendations,
        scores_json=scores_json,
        overall_score=overall_score,
        full_audio_filename=output_blob_name or '',
        document_names=document_names,
        has_error=has_error,
    )


def update_statistics(
    db_session: 'DBSession',
    conversation: Optional[ConversationScenarioRead],
    goals: GoalsAchievedCollection,
    overall_score: float,
    has_error: bool,
) -> FeedbackStatusEnum:
    """Update user profile and admin dashboard stats, handle commit/rollback."""
    if conversation and conversation.scenario and conversation.scenario.user_id:
        user = db_session.exec(
            select(UserProfile).where(UserProfile.id == conversation.scenario.user_id)
        ).first()
    else:
        user = None

    admin_stats = db_session.exec(select(AdminDashboardStats)).first()
    try:
        if user:
            user.score_sum += overall_score
            user.total_sessions += 1
            user.goals_achieved += len(goals.goals_achieved)
            db_session.add(user)
        if admin_stats:
            admin_stats.score_sum += overall_score
            admin_stats.total_trainings += 1
            db_session.add(admin_stats)
        db_session.commit()
        status = FeedbackStatusEnum.completed if not has_error else FeedbackStatusEnum.failed
    except Exception as e:
        db_session.rollback()
        status = FeedbackStatusEnum.failed
        has_error = True
        logging.error('Failed to update statistics: %s', e)
    return status


def save_session_feedback(
    db_session: 'DBSession',
    session_id: UUID,
    feedback_generation_result: FeedbackGenerationResult,
    status: FeedbackStatusEnum,
) -> SessionFeedback:
    """Build and save the SessionFeedback record."""
    feedback = SessionFeedback(
        id=uuid4(),
        session_id=session_id,
        scores=feedback_generation_result.scores_json,
        tone_analysis={},
        overall_score=feedback_generation_result.overall_score,
        transcript_uri='',
        full_audio_filename=feedback_generation_result.full_audio_filename,
        document_names=feedback_generation_result.document_names,
        speak_time_percent=0,
        questions_asked=0,
        session_length_s=0,
        goals_achieved=feedback_generation_result.goals.goals_achieved,
        example_positive=[ex.model_dump() for ex in feedback_generation_result.examples_positive],
        example_negative=[ex.model_dump() for ex in feedback_generation_result.examples_negative],
        recommendations=[rec.model_dump() for rec in feedback_generation_result.recommendations],
        status=status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(feedback)
    db_session.commit()
    return feedback


def get_conversation_data(db_session: DBSession, session_id: UUID) -> ConversationScenarioRead:
    """
    Get conversation data from the database in a single transaction.
    """
    with db_session.begin():
        session = db_session.exec(select(Session).where(Session.id == session_id)).first()
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        scenario = db_session.exec(
            select(ConversationScenario).where(ConversationScenario.id == session.scenario_id)
        ).first()
        if not scenario:
            raise HTTPException(status_code=404, detail='Conversation Scenario not found')
        scenario_read = ConversationScenario.model_validate(scenario)
        turns = db_session.exec(
            select(SessionTurn).where(SessionTurn.session_id == session_id)
        ).all()
        transcript = [SessionTurnRead.model_validate(turn) for turn in turns]
        return ConversationScenarioRead(scenario=scenario_read, transcript=transcript)


def generate_and_store_feedback(
    session_id: UUID,
    feedback_request: FeedbackRequest,
    db_session: DBSession,
    scoring_service: Optional[ScoringService] = None,
    session_turn_service: Optional[SessionTurnService] = None,
) -> SessionFeedback:
    """
    Generates feedback for a given session, stores it in the database, and returns the resulting
    SessionFeedback object. This function prepares the necessary requests and context for
    feedback generation, retrieves conversation data, and uses the provided or default scoring
    service to generate feedback components. It then updates session statistics,
    saves the generated feedback to the database, and returns the saved feedback.
    """
    if scoring_service is None:
        scoring_service = get_scoring_service()

    if session_turn_service is None:
        session_turn_service = SessionTurnService(db_session)

    goals_request, recommendations_request = prepare_feedback_requests(feedback_request)
    hr_docs_context, document_names = get_hr_docs_context(recommendations_request)

    conversation = get_conversation_data(db_session, session_id)

    if feedback_request.transcript is None:
        feedback_generation_result = FeedbackGenerationResult()
    else:
        feedback_generation_result = generate_feedback_components(
            feedback_request=feedback_request,
            goals_request=goals_request,
            hr_docs_context=hr_docs_context,
            document_names=document_names,
            conversation=conversation,
            scoring_service=scoring_service,
            session_turn_service=session_turn_service,
            session_id=session_id,
        )

    status: FeedbackStatusEnum = update_statistics(
        db_session,
        conversation,
        feedback_generation_result.goals,
        feedback_generation_result.overall_score,
        feedback_generation_result.has_error,
    )

    feedback: SessionFeedback = save_session_feedback(
        db_session,
        session_id,
        feedback_generation_result,
        status,
    )
    return feedback
