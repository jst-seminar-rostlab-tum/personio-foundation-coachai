from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session as DBSession
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import ConversationScenarioCreate, ConversationScenarioRead
from app.schemas.scenario_preparation import ScenarioPreparationRead
from app.services.conversation_scenario_service import (
    create_conversation_scenario,
    get_conversation_scenario_by_id,
    get_scenario_preparation,
    initialize_preparation,
    start_preparation_task,
    validate_category,
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
    # Validate category
    category = validate_category(conversation_scenario.category_id, db_session)

    # Create conversation scenario
    new_conversation_scenario = create_conversation_scenario(
        conversation_scenario, user_profile, db_session
    )

    # Initialize preparation
    prep = initialize_preparation(new_conversation_scenario.id, db_session)

    # Start background task for preparation
    start_preparation_task(prep.id, new_conversation_scenario, category, background_tasks)

    # Return response
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
    # Validate conversation scenario
    conversation_scenario = get_conversation_scenario_by_id(scenario_id, user_profile, db_session)

    # Fetch scenario preparation
    scenario_preparation = get_scenario_preparation(scenario_id, conversation_scenario, db_session)

    return scenario_preparation
