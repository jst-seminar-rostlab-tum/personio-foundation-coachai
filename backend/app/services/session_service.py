from datetime import UTC, datetime
from math import ceil
from typing import Optional
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import col, func, select

from app.connections.gcs_client import get_gcs_audio_manager
from app.enums.account_role import AccountRole
from app.enums.feedback_status import FeedbackStatus
from app.enums.scenario_preparation_status import ScenarioPreparationStatus
from app.enums.session_status import SessionStatus
from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.scenario_preparation import ScenarioPreparation
from app.models.session import Session
from app.models.session_feedback import SessionFeedback
from app.models.session_turn import SessionTurn
from app.models.user_profile import UserProfile
from app.schemas.session import SessionCreate, SessionDetailsRead, SessionRead, SessionUpdate
from app.schemas.session_feedback import FeedbackRequest, SessionFeedbackMetrics
from app.schemas.sessions_paginated import PaginatedSessionsResponse, SessionItem, SkillScores
from app.services.review_service import ReviewService
from app.services.session_feedback.session_feedback_service import generate_and_store_feedback
from app.services.session_turn_service import SessionTurnService


class SessionService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.gcs_audio_manager = get_gcs_audio_manager()

    def fetch_session_details(
        self, session_id: UUID, user_profile: UserProfile
    ) -> SessionDetailsRead:
        session = self._get_session(session_id)
        scenario = self._get_conversation_scenario(session.scenario_id)
        self._authorize_access(scenario, user_profile, session.allow_admin_access)

        title = self._get_training_title(scenario)
        goals = scenario.preparation.objectives if scenario.preparation else []

        # Check if the user has reviewed this session
        review_service = ReviewService(self.db)
        user_has_reviewed = review_service.has_user_reviewed_session(session_id, user_profile.id)

        session_response = SessionDetailsRead(
            id=session.id,
            scenario_id=session.scenario_id,
            scheduled_at=session.scheduled_at,
            started_at=session.started_at,
            ended_at=session.ended_at,
            status=session.status,
            allow_admin_access=session.allow_admin_access,
            created_at=session.created_at,
            updated_at=session.updated_at,
            title=title,
            has_reviewed=user_has_reviewed,
            summary='The person giving feedback was rude but the person '
            'receiving feedback took it well.',
            goals_total=goals,
        )

        session_response.feedback = self._get_session_feedback(session_id)

        return session_response

    def fetch_paginated_sessions(
        self,
        user_profile: UserProfile,
        page: int,
        page_size: int,
        scenario_id: Optional[UUID] = None,
    ) -> PaginatedSessionsResponse:
        if scenario_id:
            scenario = self._validate_scenario_access(scenario_id, user_profile)
            scenario_ids = [scenario.id]
        else:
            scenario_ids = self._get_user_scenario_ids(user_profile.id)

        if not scenario_ids:
            return PaginatedSessionsResponse(
                page=page, limit=page_size, total_pages=0, total_sessions=0, sessions=[]
            )

        total_sessions = self._count_sessions(scenario_ids)
        if total_sessions == 0:
            return PaginatedSessionsResponse(
                page=page, limit=page_size, total_pages=0, total_sessions=0, sessions=[]
            )

        sessions = self._get_sessions_paginated(scenario_ids, page, page_size)
        session_list = [self._build_session_item(sess) for sess in sessions]

        return PaginatedSessionsResponse(
            page=page,
            limit=page_size,
            total_pages=ceil(total_sessions / page_size),
            total_sessions=total_sessions,
            sessions=session_list,
        )

    def create_new_session(
        self, session_data: SessionCreate, user_profile: UserProfile
    ) -> SessionRead:
        conversation_scenario = self.db.get(ConversationScenario, session_data.scenario_id)
        if not conversation_scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')
        if (
            conversation_scenario.user_id != user_profile.id
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(
                status_code=403,
                detail='You do not have permission to create a session for this scenario',
            )
        new_session = Session(**session_data.model_dump())
        new_session.status = SessionStatus.started
        new_session.started_at = datetime.now(UTC)

        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return SessionRead(**new_session.model_dump())

    def update_existing_session(
        self,
        session_id: UUID,
        updated_data: SessionUpdate,
        user_profile: UserProfile,
        background_tasks: BackgroundTasks,
    ) -> SessionRead:
        session = self.db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

        if (
            session.status == SessionStatus.completed
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(status_code=400, detail='A completed session cannot be updated.')

        previous_status = session.status

        scenario_id = updated_data.scenario_id or session.scenario_id
        conversation_scenario = self.db.get(ConversationScenario, scenario_id)
        if not conversation_scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(session, key, value)

        if self._is_session_being_completed(previous_status, updated_data.status, session.feedback):
            self._handle_completion(session, conversation_scenario, user_profile, background_tasks)

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return SessionRead(**session.model_dump())

    def delete_all_user_sessions(self, user_profile: UserProfile) -> dict:
        user_id = user_profile.id
        statement = select(ConversationScenario).where(ConversationScenario.user_id == user_id)
        conversation_scenarios = self.db.exec(statement).all()
        if not conversation_scenarios:
            return {
                'message': f'No sessions found for user ID {user_id}',
                'audios': [],
            }

        total_deleted_sessions = 0
        audio_uris = []
        for scenario in conversation_scenarios:
            for session in scenario.sessions:
                for turn in session.session_turns:
                    if turn.audio_uri:
                        audio_uris.append(turn.audio_uri)
                        total_deleted_sessions += 1
        # Let the database handle cascade deletes by just deleting the scenarios
        for scenario in conversation_scenarios:
            self.db.delete(scenario)
        self.db.commit()

        # TODO: Delete audio File self._delete_audio_files(audio_uris)
        self._delete_audio_files(audio_uris=audio_uris)  # Dummy function to delete audios
        return {
            'message': f'Deleted {total_deleted_sessions} sessions for user ID {user_id}',
            'audios': audio_uris,
        }

    def delete_session_by_id(self, session_id: UUID, user_profile: UserProfile) -> dict:
        session = self.db.exec(select(Session).where(Session.id == session_id)).first()
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')
        if (
            session.scenario.user_id != user_profile.id
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(
                status_code=403, detail='You do not have permission to delete this session'
            )
        # TODO: Delete audio File self._delete_audio_files(session.audio_uris)
        total_deleted_sessions = 0
        audio_uris = []
        for turn in session.session_turns:
            if turn.audio_uri:
                audio_uris.append(turn.audio_uri)
                total_deleted_sessions += 1
        # TODO: Delete audio File self._delete_audio_files(audio_uris)
        self._delete_audio_files(audio_uris=audio_uris)  # Dummy function to delete audios

        self.db.delete(session)
        self.db.commit()
        return {
            'message': 'Session deleted successfully',
            'audios': audio_uris,
        }

    def _is_session_being_completed(
        self,
        previous_status: SessionStatus,
        updated_status: SessionStatus | None,
        feedback: SessionFeedback | None,
    ) -> bool:
        """
        Helper function to check if the session is transitioning to 'completed' status
        and has no feedback associated with it.
        """
        return (
            previous_status != SessionStatus.completed
            and updated_status == SessionStatus.completed
            and feedback is None
        )

    def _handle_completion(
        self,
        session: Session,
        conversation_scenario: ConversationScenario,
        user_profile: UserProfile,
        background_tasks: BackgroundTasks,
    ) -> None:
        """
        Handle the logic for completing a session, including generating feedback,
        updating user statistics, and admin dashboard stats.
        """
        session.ended_at = datetime.now(UTC)

        # Fetch preparation for the session
        statement = select(ScenarioPreparation).where(
            ScenarioPreparation.scenario_id == session.scenario_id
        )
        preparation = self.db.exec(statement).first()
        if not preparation:
            raise HTTPException(
                status_code=400, detail='No preparation steps found for the given scenario'
            )
        if preparation.status != ScenarioPreparationStatus.completed:
            raise HTTPException(
                status_code=400,
                detail='Preparation steps must be completed before generating feedback',
            )

        # Fetch session turns and generate transcript
        session_turns = self.db.exec(
            select(SessionTurn).where(SessionTurn.session_id == session.id)
        ).all()
        transcripts = None
        if session_turns:
            transcripts = '\n'.join([f'{turn.speaker}: {turn.text}' for turn in session_turns])

        # Fetch conversation category
        category = None
        if conversation_scenario.category_id is not None:
            category = self.db.exec(
                select(ConversationCategory).where(
                    ConversationCategory.id == conversation_scenario.category_id
                )
            ).first()
            if not category:
                raise HTTPException(
                    status_code=404, detail='Conversation category not found for the session'
                )

        # Use the helper function to update user stats and schedule feedback
        self._update_user_stats(
            session=session,
            user_profile=user_profile,
            background_tasks=background_tasks,
            conversation_scenario=conversation_scenario,
            preparation=preparation,
            transcripts=transcripts,
            category=category,
        )

    def _update_user_stats(
        self,
        session: Session,
        user_profile: UserProfile,
        background_tasks: BackgroundTasks,
        conversation_scenario: ConversationScenario,
        preparation: ScenarioPreparation,
        transcripts: str | None,
        category: ConversationCategory | None,
    ) -> None:
        """
        Update user statistics, schedule feedback generation, and update admin dashboard stats.
        """
        # Prepare key concepts string
        key_concepts = preparation.key_concepts

        key_concepts_str = '\n'.join(f'{item["header"]}: {item["value"]}' for item in key_concepts)

        request = FeedbackRequest(
            category=category.name
            if category
            else conversation_scenario.custom_category_label or 'Unknown Category',
            persona=conversation_scenario.persona,
            situational_facts=conversation_scenario.situational_facts,
            transcript=transcripts,
            objectives=preparation.objectives,
            key_concepts=key_concepts_str,
        )

        background_tasks.add_task(
            generate_and_store_feedback,
            session_id=session.id,
            feedback_request=request,
            db_session=self.db,
        )

        # Calculate session length
        started_at = (
            session.started_at.replace(tzinfo=UTC)
            if session.started_at and session.started_at.tzinfo is None
            else session.started_at
        )
        ended_at = (
            session.ended_at.replace(tzinfo=UTC)
            if session.ended_at and session.ended_at.tzinfo is None
            else session.ended_at
        )

        if ended_at and started_at:
            session_length = (ended_at - started_at).total_seconds() / 3600  # in hours
        else:
            session_length = 0  # Default to 0 if either datetime is None
        user_profile.total_sessions = (user_profile.total_sessions or 0) + 1
        user_profile.training_time = (user_profile.training_time or 0) + session_length
        user_profile.updated_at = datetime.now(UTC)
        self.db.add(user_profile)

        stats = self.db.exec(select(AdminDashboardStats)).first()
        if not stats:
            stats = AdminDashboardStats()
            self.db.add(stats)
        stats.total_trainings = (stats.total_trainings or 0) + 1

    def _get_session(self, session_id: UUID) -> Session:
        session = self.db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail='No session found with the given ID')
        return session

    def _get_conversation_scenario(self, scenario_id: UUID) -> ConversationScenario:
        scenario = self.db.get(ConversationScenario, scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=404, detail='No conversation scenario found for the session'
            )
        return scenario

    def _authorize_access(
        self, scenario: ConversationScenario, user_profile: UserProfile, allow_admin_access: bool
    ) -> None:
        if scenario.user_id != user_profile.id and user_profile.account_role != AccountRole.admin:
            raise HTTPException(
                status_code=403, detail='You do not have permission to access this session'
            )
        if (
            scenario.user_id != user_profile.id
            and user_profile.account_role == AccountRole.admin
            and not allow_admin_access
        ):
            raise HTTPException(
                status_code=403,
                detail='You do not have permission to access this session as an admin',
            )

    def _get_training_title(self, scenario: ConversationScenario) -> str:
        if scenario.category:
            return scenario.category.name
        if scenario.custom_category_label:
            return scenario.custom_category_label
        return 'No Title available'

    def _get_session_feedback(self, session_id: UUID) -> SessionFeedbackMetrics | None:
        feedback = self.db.exec(
            select(SessionFeedback).where(SessionFeedback.session_id == session_id)
        ).first()
        if not feedback or feedback.status == FeedbackStatus.pending:
            raise HTTPException(status_code=202, detail='Session feedback in progress.')
        if feedback.status == FeedbackStatus.failed:
            raise HTTPException(status_code=500, detail='Session feedback failed.')

        audio_file_exists = False

        if self.gcs_audio_manager is not None:
            audio_file_exists = self.gcs_audio_manager.document_exists(
                filename=feedback.full_audio_filename
            )
        if audio_file_exists:
            full_audio_url = self.gcs_audio_manager.generate_signed_url(
                filename=feedback.full_audio_filename,
            )
        else:
            full_audio_url = None

        session_turn_service = SessionTurnService(self.db)
        session_turn_transcripts = session_turn_service.get_session_turns(session_id=session_id)

        return SessionFeedbackMetrics(
            scores=feedback.scores,
            tone_analysis=feedback.tone_analysis,
            overall_score=feedback.overall_score,
            transcript_uri=feedback.transcript_uri,
            speak_time_percent=feedback.speak_time_percent,
            questions_asked=feedback.questions_asked,
            session_length_s=feedback.session_length_s,
            goals_achieved=feedback.goals_achieved,
            example_positive=feedback.example_positive,  # type: ignore
            example_negative=feedback.example_negative,  # type: ignore
            recommendations=feedback.recommendations,  # type: ignore
            full_audio_url=full_audio_url,
            document_names=feedback.document_names,
            session_turn_transcripts=session_turn_transcripts,
        )

    def _get_user_scenario_ids(self, user_id: UUID) -> list[UUID]:
        result = self.db.exec(
            select(ConversationScenario.id).where(ConversationScenario.user_id == user_id)
        ).all()
        return list(result)

    def _count_sessions(self, scenario_ids: list[UUID]) -> int:
        return self.db.exec(
            select(func.count()).where(col(Session.scenario_id).in_(scenario_ids))
        ).one()

    def _get_sessions_paginated(
        self, scenario_ids: list[UUID], page: int, page_size: int
    ) -> list[Session]:
        sessions = self.db.exec(
            select(Session)
            .where(col(Session.scenario_id).in_(scenario_ids))
            .order_by(col(Session.created_at).desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(sessions)

    def _build_session_item(self, sess: Session) -> SessionItem:
        scenario = self.db.exec(
            select(ConversationScenario).where(ConversationScenario.id == sess.scenario_id)
        ).first()
        if not scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

        category = (
            self.db.exec(
                select(ConversationCategory).where(ConversationCategory.id == scenario.category_id)
            ).first()
            if scenario.category_id
            else None
        )

        title = category.name if category else 'No Title'
        summary = category.name if category else 'No Summary'
        feedback = sess.feedback

        scores = (
            SkillScores(
                structure=feedback.scores.get('structure', -1) if feedback else -1,
                empathy=feedback.scores.get('empathy', -1) if feedback else -1,
                focus=feedback.scores.get('focus', -1) if feedback else -1,
                clarity=feedback.scores.get('clarity', -1) if feedback else -1,
            )
            if feedback
            else SkillScores(structure=-1, empathy=-1, focus=-1, clarity=-1)
        )

        return SessionItem(
            session_id=sess.id,
            title=title,
            summary=summary,
            status=sess.status,
            date=sess.ended_at,
            overall_score=feedback.overall_score if feedback else -1,
            skills=scores,
            allow_admin_access=sess.allow_admin_access,
        )

    def _delete_audio_files(self, audio_uris: list[str]) -> None:
        """Mock function to delete audio files from object storage.
        Replace this with your actual object storage client logic."""
        for uri in audio_uris:  # TODO: delete audios on object storage.  # noqa: B007
            pass

    def _validate_scenario_access(
        self, scenario_id: UUID, user_profile: UserProfile
    ) -> ConversationScenario:
        """
        Validate access to a specific conversation scenario.
        Ensures the scenario exists and the user has permission to access it.
        """
        scenario = self.db.get(ConversationScenario, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail='Scenario not found')
        if scenario.user_id != user_profile.id and user_profile.account_role != AccountRole.admin:
            raise HTTPException(
                status_code=403, detail='You do not have permission to access this scenario'
            )
        return scenario
