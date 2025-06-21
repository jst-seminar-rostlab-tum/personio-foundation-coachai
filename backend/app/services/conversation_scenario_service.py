from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import ConversationScenarioCreate
from app.schemas.scenario_preparation import ScenarioPreparationCreate, ScenarioPreparationRead
from app.services.scenario_preparation_service import (
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
    ) -> JSONResponse:
        """
        Create a new conversation scenario and start the preparation process in the background.
        """
        # Validate category
        category = self._validate_category(conversation_scenario.category_id)

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

        # Return a JSONResponse
        return JSONResponse(
            status_code=202,
            content={
                'message': 'Conversation scenario created, preparation started.',
                'scenarioId': str(new_conversation_scenario.id),
            },
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
            and user_profile.account_role != 'admin'
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
            context=conversation_scenario.context,
            goal=conversation_scenario.goal,
            other_party=conversation_scenario.other_party,
            category_name=category_name,
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
            context=conversation_scenario.context,
            goal=conversation_scenario.goal,
            other_party=conversation_scenario.other_party,
            num_objectives=3,  # Example value, adjust as needed
            num_checkpoints=3,  # Example value, adjust as needed
        )
        background_tasks.add_task(
            generate_scenario_preparation, prep_id, new_preparation, get_db_session
        )
