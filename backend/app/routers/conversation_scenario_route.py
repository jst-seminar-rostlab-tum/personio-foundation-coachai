from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import ConversationScenarioCreate
from app.schemas.scenario_preparation import ScenarioPreparationRead
from app.services.conversation_scenario_service import ConversationScenarioService

router = APIRouter(prefix='/conversation-scenario', tags=['Conversation Scenarios'])


def get_conversation_scenario_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ConversationScenarioService:
    """
    Dependency factory to inject the ConversationScenarioService.
    """
    return ConversationScenarioService(db_session)


@router.post('', response_model=None, dependencies=[Depends(require_user)])
def create_conversation_scenario_with_preparation(
    conversation_scenario: ConversationScenarioCreate,
    background_tasks: BackgroundTasks,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> JSONResponse:
    """
    Create a new conversation scenario and start the preparation process in the background.
    """
    return service.create_conversation_scenario_with_preparation(
        conversation_scenario, user_profile, background_tasks
    )


@router.get('/{scenario_id}/preparation', response_model=ScenarioPreparationRead)
def get_scenario_preparation_by_scenario_id(
    scenario_id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> ScenarioPreparationRead:
    """
    Retrieve the scenario preparation data for a given conversation scenario ID.
    """
    return service.get_scenario_preparation_by_scenario_id(scenario_id, user_profile)
