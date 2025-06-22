from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.scenario_preparation import (
    ScenarioPreparation,
    ScenarioPreparationStatus,
)
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import (
    ConversationScenarioCreate,
    ConversationScenarioRead,
)
from app.schemas.scenario_preparation import ScenarioPreparationCreate, ScenarioPreparationRead
from app.services.scenario_preparation_service import (
    create_pending_preparation,
    generate_scenario_preparation,
)

router = APIRouter(prefix='/conversation-scenario', tags=['Conversation Scenarios'])


@router.post('', response_model=ConversationScenarioRead, dependencies=[Depends(require_user)])
def create_conversation_scenario_with_preparation(
    conversation_scenario: ConversationScenarioCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
    user_profile: Annotated[UserProfile, Depends(require_user)],
) -> JSONResponse:
    """
    Create a new conversation scenario and start the preparation process in the background.
    """
    category = None
    # 1. Validate foreign keys
    if conversation_scenario.category_id:
        category = db_session.get(ConversationCategory, conversation_scenario.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    # 2. Create new ConversationScenario, set user_id from user_profile
    new_conversation_scenario = ConversationScenario(
        **conversation_scenario.model_dump(), user_id=user_profile.id
    )
    db_session.add(new_conversation_scenario)
    db_session.commit()
    db_session.refresh(new_conversation_scenario)

    # 3. Initialize preparation（status = pending）
    prep = create_pending_preparation(new_conversation_scenario.id, db_session)

    new_preparation = ScenarioPreparationCreate(
        category=category.name if category else '',
        context=new_conversation_scenario.context,
        goal=new_conversation_scenario.goal,
        other_party=new_conversation_scenario.other_party,
        num_objectives=3,  # Example value, adjust as needed
        num_checkpoints=3,  # Example value, adjust as needed
        language_code=new_conversation_scenario.language_code,
    )

    # 4. Start background task to generate preparation
    background_tasks.add_task(
        generate_scenario_preparation, prep.id, new_preparation, get_db_session
    )
    # 5. Return response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'Conversation scenario created, preparation started.',
            'scenarioId': str(new_conversation_scenario.id),
        },
    )


@router.get(
    '/{scenario_id}/preparation',
    response_model=ScenarioPreparationRead,
)
def get_scenario_preparation_by_scenario_id(
    scenario_id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ScenarioPreparationRead:
    """
    Retrieve the scenario preparation data for a given conversation scenario ID.
    """
    # Validate that the conversation scenario exists
    conversation_scenario = db_session.get(ConversationScenario, scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    if conversation_scenario.user_id != user_profile.id and user_profile.account_role != 'admin':
        raise HTTPException(
            status_code=400,
            detail='You do not have permission to access this scenario, '
            'you can only view your own scenarios.',
        )

    # Fetch the associated scenario preparation
    statement = select(ScenarioPreparation).where(ScenarioPreparation.scenario_id == scenario_id)
    scenario_preparation = db_session.exec(statement).first()

    print(f'Scenario Preparation: {scenario_preparation}')

    if not scenario_preparation or scenario_preparation.status == ScenarioPreparationStatus.pending:
        raise HTTPException(status_code=202, detail='Session preparation in progress.')

    elif scenario_preparation.status == ScenarioPreparationStatus.failed:
        raise HTTPException(status_code=500, detail='Session preparation failed.')

    # Prepare category name with fallback to custom label or None
    category_name = (
        conversation_scenario.category.name
        if conversation_scenario.category
        else conversation_scenario.custom_category_label
        if conversation_scenario.custom_category_label
        else None
    )

    # Return the scenario preparation read model with additional scenario context
    return ScenarioPreparationRead(
        **scenario_preparation.model_dump(),
        context=conversation_scenario.context,
        goal=conversation_scenario.goal,
        other_party=conversation_scenario.other_party,
        category_name=category_name,
    )
