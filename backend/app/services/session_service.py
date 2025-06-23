from datetime import UTC, datetime
from math import ceil
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import col, func, select

from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.session import Session, SessionStatus
from app.models.session_feedback import FeedbackStatusEnum, SessionFeedback
from app.models.session_turn import SessionTurn
from app.models.user_profile import AccountRole, UserProfile
from app.schemas.session import SessionCreate, SessionDetailsRead, SessionRead, SessionUpdate
from app.schemas.session_feedback import ExamplesRequest, SessionFeedbackMetrics
from app.schemas.sessions_paginated import PaginatedSessionsResponse, SessionItem, SkillScores
from app.services.session_feedback_service import generate_and_store_feedback


class SessionService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def fetch_session_details(
        self, session_id: UUID, user_profile: UserProfile
    ) -> SessionDetailsRead:
        session = self.db.get(Session, session_id)
        if not session:
            raise HTTPException(status_code=404, detail='No session found with the given ID')

        conversation_scenario = self.db.get(ConversationScenario, session.scenario_id)
        if not conversation_scenario:
            raise HTTPException(
                status_code=404, detail='No conversation scenario found for the session'
            )

        if (
            conversation_scenario.user_id != user_profile.id
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(
                status_code=403, detail='You do not have permission to access this session'
            )

        training_title = (
            conversation_scenario.category.name
            if conversation_scenario.category
            else conversation_scenario.custom_category_label
            if conversation_scenario.custom_category_label
            else 'No Title available'
        )

        goals = (
            conversation_scenario.preparation.objectives
            if conversation_scenario.preparation
            else []
        )

        session_response = SessionDetailsRead(
            id=session.id,
            scenario_id=session.scenario_id,
            scheduled_at=session.scheduled_at,
            started_at=session.started_at,
            ended_at=session.ended_at,
            ai_persona=session.ai_persona,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            title=training_title,
            summary='The person giving feedback was rude but the person receiving feedback/'
            ' took it well.',  # mocked
            goals_total=goals,
        )

        session_turns = self.db.exec(
            select(SessionTurn).where(SessionTurn.session_id == session_id)
        ).all()
        if session_turns:
            session_response.audio_uris = [turn.audio_uri for turn in session_turns]

        feedback = self.db.exec(
            select(SessionFeedback).where(SessionFeedback.session_id == session_id)
        ).first()
        if not feedback or feedback.status == FeedbackStatusEnum.pending:
            raise HTTPException(status_code=202, detail='Session feedback in progress.')
        elif feedback.status == FeedbackStatusEnum.failed:
            raise HTTPException(status_code=500, detail='Session feedback failed.')
        else:
            session_response.feedback = SessionFeedbackMetrics(
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
            )

        return session_response

    def fetch_paginated_sessions(
        self, user_profile: UserProfile, page: int, page_size: int
    ) -> PaginatedSessionsResponse:
        user_id = user_profile.id
        scenario_ids = self.db.exec(
            select(ConversationScenario.id).where(ConversationScenario.user_id == user_id)
        ).all()

        if not scenario_ids:
            return PaginatedSessionsResponse(
                page=page, limit=page_size, total_pages=0, total_sessions=0, sessions=[]
            )

        total_sessions = self.db.exec(
            select(func.count()).where(col(Session.scenario_id).in_(scenario_ids))
        ).one()

        if total_sessions == 0:
            return PaginatedSessionsResponse(
                page=page,
                limit=page_size,
                total_pages=0,
                total_sessions=0,
                sessions=[],
            )

        sessions = self.db.exec(
            select(Session)
            .where(col(Session.scenario_id).in_(scenario_ids))
            .order_by(col(Session.created_at).desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        session_list = []
        for sess in sessions:
            conversation_scenario = self.db.exec(
                select(ConversationScenario).where(ConversationScenario.id == sess.scenario_id)
            ).first()
            if not conversation_scenario:
                raise HTTPException(status_code=404, detail='Conversation scenario not found')

            conversation_category = None
            if conversation_scenario.category_id:
                conversation_category = self.db.exec(
                    select(ConversationCategory).where(
                        ConversationCategory.id == conversation_scenario.category_id
                    )
                ).first()
                if not conversation_category:
                    raise HTTPException(status_code=404, detail='Conversation Category not found')

            item = SessionItem(
                session_id=sess.id,
                title=conversation_category.name if conversation_category else 'No Title',
                summary=conversation_category.name if conversation_category else 'No Summary',
                status=sess.status,
                date=sess.ended_at,
                score=sess.feedback.overall_score if sess.feedback else -1,  # mocked
                skills=SkillScores(
                    structure=sess.feedback.scores['structure']
                    if sess.feedback and 'structure' in sess.feedback.scores
                    else -1,
                    empathy=sess.feedback.scores['empathy']
                    if sess.feedback and 'empathy' in sess.feedback.scores
                    else -1,
                    solution_focus=sess.feedback.scores['solutionFocus']
                    if sess.feedback and 'solutionFocus' in sess.feedback.scores
                    else -1,
                    clarity=sess.feedback.scores['clarity']
                    if sess.feedback and 'clarity' in sess.feedback.scores
                    else -1,
                )
                if sess.feedback
                else SkillScores(structure=-1, empathy=-1, solution_focus=-1, clarity=-1),
            )
            session_list.append(item)

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
            raise HTTPException(status_code=404, detail='No sessions found for the given user ID')

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
        self.db.delete(session)
        self.db.commit()
        return {'message': 'Session deleted successfully'}

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

        request = ExamplesRequest(
            category=category.name
            if category
            else conversation_scenario.custom_category_label or 'Unknown Category',
            goal=conversation_scenario.goal,
            context=conversation_scenario.context,
            other_party=conversation_scenario.other_party,
            transcript=transcripts,
            objectives=preparation.objectives,
            key_concepts=key_concepts_str,
        )

        background_tasks.add_task(
            generate_and_store_feedback,
            session_id=session.id,
            example_request=request,
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
