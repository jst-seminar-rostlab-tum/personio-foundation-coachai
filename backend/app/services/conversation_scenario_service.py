from typing import Optional
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session, select

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


def validate_category(
    category_id: Optional[str], db_session: Session
) -> ConversationCategory | None:
    """
    Validate that the category exists in the database.
    """
    if category_id:
        category = db_session.get(ConversationCategory, category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')
        return category
    return None


def create_conversation_scenario(
    conversation_scenario: ConversationScenarioCreate,
    user_profile: UserProfile,
    db_session: Session,
) -> ConversationScenario:
    """
    Create a new conversation scenario and associate it with the user profile.
    """
    new_conversation_scenario = ConversationScenario(
        **conversation_scenario.model_dump(), user_id=user_profile.id
    )
    db_session.add(new_conversation_scenario)
    db_session.commit()
    db_session.refresh(new_conversation_scenario)
    return new_conversation_scenario


def initialize_preparation(scenario_id: UUID, db_session: Session) -> ScenarioPreparation:
    """
    Initialize a pending preparation for the given scenario ID.
    """
    return create_pending_preparation(scenario_id, db_session)


def start_preparation_task(
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


def get_conversation_scenario_by_id(
    scenario_id: UUID,
    user_profile: UserProfile,
    db_session: Session,
) -> ConversationScenario:
    """
    Retrieve a conversation scenario by ID and validate permissions.
    """
    conversation_scenario = db_session.get(ConversationScenario, scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    if conversation_scenario.user_id != user_profile.id and user_profile.account_role != 'admin':
        raise HTTPException(
            status_code=400,
            detail='You do not have permission to access this scenario, '
            'you can only view your own scenarios.',
        )
    return conversation_scenario


def get_scenario_preparation(
    scenario_id: UUID,
    conversation_scenario: ConversationScenario,
    db_session: Session,
) -> ScenarioPreparationRead:
    """
    Fetch the scenario preparation data for a given scenario ID.
    """
    statement = select(ScenarioPreparation).where(ScenarioPreparation.scenario_id == scenario_id)
    scenario_preparation = db_session.exec(statement).first()

    if not scenario_preparation or scenario_preparation.status == ScenarioPreparationStatus.pending:
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
