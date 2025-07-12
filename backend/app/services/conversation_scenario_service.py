from collections.abc import Sequence
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import func, select

from app.database import get_db_session
from app.enums.account_role import AccountRole
from app.enums.language import LanguageCode
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario, DifficultyLevel
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.session import Session
from app.models.session_feedback import FeedbackStatus, SessionFeedback
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import (
    ConversationScenarioConfirm,
    ConversationScenarioCreate,
    ConversationScenarioSummary,
)
from app.schemas.scenario_preparation import ScenarioPreparationCreate, ScenarioPreparationRead
from app.services.scenario_preparation.scenario_preparation_service import (
    create_pending_preparation,
    generate_scenario_preparation,
)


class ConversationScenarioService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create_conversation_scenario_with_preparation(
        self,
        conversation_scenario: ConversationScenarioCreate,
        user_profile: UserProfile,
        background_tasks: BackgroundTasks,
        custom_scenario: bool = False,
    ) -> ConversationScenarioConfirm:
        """
        Create a new conversation scenario and start the preparation process in the background.

        """
        # Validate category
        category = self._validate_category(conversation_scenario.category_id)

        # Check need for creating a new conversation scenario
        # if custom_scenario is True, we assume the scenario is custom and needs to be created.
        if not custom_scenario:
            # Check if there is an existing scenario with the same category, language and difficulty
            existing_scenarios = self._get_scenarios_by_category_language_difficulty(
                user_profile.id,
                conversation_scenario.category_id,
                conversation_scenario.language_code,
                conversation_scenario.difficulty_level,
            )
            if len(existing_scenarios) > 0:
                equal_scenario_id = self._get_equal_scenario(
                    existing_scenarios, conversation_scenario
                )
                if equal_scenario_id:
                    return ConversationScenarioConfirm(
                        message='Conversation scenario with the same prompt already exists.',
                        scenario_id=equal_scenario_id,
                    )

        # Create conversation scenario
        new_conversation_scenario = ConversationScenario(
            **conversation_scenario.model_dump(), user_id=user_profile.id
        )
        self.db.add(new_conversation_scenario)
        self.db.commit()
        self.db.refresh(new_conversation_scenario)

        # Initialize preparation
        prep = create_pending_preparation(new_conversation_scenario.id, self.db)

        # Start background task for preparation
        self._start_preparation_task(prep.id, new_conversation_scenario, category, background_tasks)

        return ConversationScenarioConfirm(
            message='Conversation scenario created, preparation started.',
            scenario_id=new_conversation_scenario.id,
        )

    def get_scenario_preparation_by_scenario_id(
        self, scenario_id: UUID, user_profile: UserProfile
    ) -> ScenarioPreparationRead:
        """
        Retrieve the scenario preparation data for a given conversation scenario ID.
        """
        conversation_scenario = self.db.get(ConversationScenario, scenario_id)
        if not conversation_scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

        if (
            conversation_scenario.user_id != user_profile.id
            and user_profile.account_role != AccountRole.admin
        ):
            raise HTTPException(
                status_code=403,
                detail='You do not have permission to access this scenario, '
                'you can only view your own scenarios.',
            )

        statement = select(ScenarioPreparation).where(
            ScenarioPreparation.scenario_id == scenario_id
        )
        scenario_preparation = self.db.exec(statement).first()

        if (
            not scenario_preparation
            or scenario_preparation.status == ScenarioPreparationStatus.pending
        ):
            raise HTTPException(status_code=202, detail='Session preparation in progress.')

        elif scenario_preparation.status == ScenarioPreparationStatus.failed:
            raise HTTPException(status_code=500, detail='Session preparation failed.')

        category_name = (
            conversation_scenario.category.name
            if conversation_scenario.category
            else conversation_scenario.custom_category_label
            if conversation_scenario.custom_category_label
            else None
        )

        return ScenarioPreparationRead(
            **scenario_preparation.model_dump(),
            category_name=category_name,
            persona=conversation_scenario.persona,
            situational_facts=conversation_scenario.situational_facts,
        )

    def list_scenarios_summary(
        self, user_profile: UserProfile
    ) -> list[ConversationScenarioSummary]:
        """
        Retrieve a summary of all conversation scenarios for the given user profile.

        The summary includes:
        - `scenario_id`: Unique identifier for the scenario.
        - `language_code`: Language code of the scenario.
        - `category_name`: Name of the category or custom category label.
        - `total_sessions`: Total number of sessions associated with the scenario.
        - `average_score`: Average score of completed session feedback.

        If the user is not an admin, only scenarios owned by the user are included.

        Args:
            user_profile (UserProfile): The profile of the user requesting the summary.

        Returns:
            list[ConversationScenarioSummary]: A list of summaries for all conversation scenarios.
        """
        stmt = (
            select(
                ConversationScenario.id.label('scenario_id'),  # type: ignore
                ConversationScenario.language_code,
                func.coalesce(
                    ConversationCategory.name,
                    ConversationScenario.custom_category_label,
                ).label('category_name'),
                func.count(func.distinct(Session.id)).label('total_sessions'),
                func.avg(SessionFeedback.overall_score).label('average_score'),
            )
            # scenario → category (may be NULL)
            .outerjoin(
                ConversationCategory,
                ConversationScenario.category_id == ConversationCategory.id,
            )
            # scenario → session  (may be zero)
            .outerjoin(Session, Session.scenario_id == ConversationScenario.id)
            # session  → feedback (may be zero)
            .outerjoin(SessionFeedback, SessionFeedback.session_id == Session.id)
            .where(
                SessionFeedback.status == FeedbackStatus.completed,
            )
            .group_by(
                ConversationScenario.id,
                ConversationScenario.language_code,
                ConversationCategory.name,
                ConversationScenario.custom_category_label,
            )
        )

        if user_profile.account_role != AccountRole.admin:
            stmt = stmt.where(ConversationScenario.user_id == user_profile.id)

        rows = self.db.exec(stmt).all()

        return [
            ConversationScenarioSummary(
                scenario_id=row.scenario_id,
                language_code=row.language_code,
                category_name=row.category_name,
                total_sessions=row.total_sessions,
                average_score=row.average_score,
            )
            for row in rows
        ]

    def delete_conversation_scenario(self, scenario_id: UUID, user_profile: UserProfile) -> dict:
        """
        Deletes a single conversation scenario by ID, ensuring cascade deletion of sessions.
        """
        user_id = user_profile.id
        scenario = self.db.get(ConversationScenario, scenario_id)
        if not scenario:
            return {
                'message': f'No scenario found for scenario ID {scenario_id}',
                'audios': [],
            }

        if scenario.user_id != user_id:
            raise HTTPException(status_code=403, detail='Not authorized to delete this scenario.')

        total_deleted_sessions = 0
        audio_uris = []
        for session in scenario.sessions:
            for turn in session.session_turns:
                if turn.audio_uri:
                    audio_uris.append(turn.audio_uri)
                    total_deleted_sessions += 1

        # TODO: Delete audio File self._delete_audio_files(audio_uris)
        self._delete_audio_files(audio_uris=audio_uris)  # Dummy function to delete audios
        self.db.delete(scenario)
        self.db.commit()
        return {
            'message': f'Deleted {total_deleted_sessions} sessions for user ID {user_id}',
            'audios': audio_uris,
        }

    def clear_all_conversation_scenarios(self, user_profile: UserProfile) -> dict:
        """
        Deletes all conversation scenarios for the authenticated user, ensuring cascade deletion of
        sessions.
        """
        user_id = user_profile.id
        statement = select(ConversationScenario).where(ConversationScenario.user_id == user_id)
        scenarios = self.db.exec(statement).all()
        if not scenarios:
            return {
                'message': f'No scenario found for user ID {user_id}',
                'audios': [],
            }

        total_deleted_scenarios = 0
        audio_uris = []
        for scenario in scenarios:
            for session in scenario.sessions:
                for turn in session.session_turns:
                    if turn.audio_uri:
                        audio_uris.append(turn.audio_uri)

        # Let the database handle cascade deletes by just deleting the scenarios
        for scenario in scenarios:
            self.db.delete(scenario)
            total_deleted_scenarios += 1
        self.db.commit()

        # TODO: Delete audio File self._delete_audio_files(audio_uris)
        self._delete_audio_files(audio_uris=audio_uris)  # Dummy function to delete audios

        self.db.commit()
        return {
            'message': f'Deleted {total_deleted_scenarios} scenario for user ID {user_id}',
            'audios': audio_uris,
        }

    def get_scenario_summary(
        self, scenario_id: UUID, user_profile: UserProfile
    ) -> ConversationScenarioSummary:
        """
        Retrieve a summary for a specific conversation scenario.

        The summary includes:
        - `scenario_id`: Unique identifier for the scenario.
        - `language_code`: Language code of the scenario.
        - `category_name`: Name of the category or custom category label.
        - `total_sessions`: Total number of sessions associated with the scenario.
        - `average_score`: Average score of completed session feedback.

        Validates that the scenario exists and that the user has permission to access it.

        Args:
            scenario_id (UUID): The unique identifier of the conversation scenario.
            user_profile (UserProfile): The profile of the user requesting the summary.

        Returns:
            ConversationScenarioSummary: A summary of the specified conversation scenario.

        Raises:
            HTTPException: If the scenario does not exist or the user does not have permission to
            access it.
        """
        scenario = self.db.get(ConversationScenario, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

        if scenario.user_id != user_profile.id and user_profile.account_role != AccountRole.admin:
            raise HTTPException(
                status_code=403,
                detail='You do not have permission to access this scenario.',
            )

        total_sessions = len(scenario.sessions) if scenario.sessions else 0
        average_score = (
            sum(
                [
                    session.feedback.overall_score
                    for session in scenario.sessions
                    if session.feedback and session.feedback.status == FeedbackStatus.completed
                ]
            )
            / total_sessions
            if total_sessions > 0
            else None
        )
        category_name = (
            scenario.category.name if scenario.category else scenario.custom_category_label or ''
        )

        return ConversationScenarioSummary(
            scenario_id=scenario.id,
            language_code=scenario.language_code,
            category_name=category_name,
            total_sessions=total_sessions,
            average_score=average_score,
        )

    def _validate_category(self, category_id: str | None) -> ConversationCategory | None:
        """
        Validate that the category exists in the database.
        """
        if category_id:
            category = self.db.get(ConversationCategory, category_id)
            if not category:
                raise HTTPException(status_code=404, detail='Category not found')
            return category
        return None

    def _get_scenarios_by_category_language_difficulty(
        self,
        user_id: UUID,
        category_id: str | None,
        language_code: LanguageCode,
        difficulty_level: DifficultyLevel,
    ) -> Sequence[ConversationScenario]:
        """
        Retrieve all conversation scenarios for a given user and category.
        """
        statement = select(ConversationScenario).where(ConversationScenario.user_id == user_id)
        if category_id:
            statement = statement.where(
                ConversationScenario.category_id == category_id,
                ConversationScenario.language_code == language_code,
                ConversationScenario.difficulty_level == difficulty_level,
            )
        return self.db.exec(statement).all()

    def _get_equal_scenario(
        self, scenarios: Sequence[ConversationScenario], new_scenario: ConversationScenarioCreate
    ) -> UUID | None:
        """
        Check if there are any existing scenarios with the same prompt as the new scenario.
        """
        for scenario in scenarios:
            if scenario.persona.replace(' ', '') == new_scenario.persona.replace(
                ' ', ''
            ) and scenario.situational_facts.replace(
                ' ', ''
            ) == new_scenario.situational_facts.replace(' ', ''):
                return scenario.id
        return None

    def _start_preparation_task(
        self,
        prep_id: UUID,
        conversation_scenario: ConversationScenario,
        category: ConversationCategory | None,
        background_tasks: BackgroundTasks,
    ) -> None:
        """
        Start the background task to generate scenario preparation.
        """
        new_preparation = ScenarioPreparationCreate(
            category=category.name if category else '',
            persona=conversation_scenario.persona,
            situational_facts=conversation_scenario.situational_facts,
            num_objectives=3,  # Example value, adjust as needed
            num_checkpoints=3,  # Example value, adjust as needed
            language_code=conversation_scenario.language_code,
        )
        background_tasks.add_task(
            generate_scenario_preparation, prep_id, new_preparation, get_db_session
        )

    def _delete_audio_files(self, audio_uris: list[str]) -> None:
        """Mock function to delete audio files from object storage.
        Replace this with your actual object storage client logic."""
        for uri in audio_uris:  # TODO: delete audios on object storage.  # noqa: B007
            pass
