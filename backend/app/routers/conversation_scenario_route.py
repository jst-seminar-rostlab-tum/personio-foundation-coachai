from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_user
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import (
    ConversationScenarioCreate,
    ConversationScenarioCreateResponse,
    ConversationScenarioSummary,
)
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


@router.get(
    '',  # /conversation-scenario
    response_model=list[ConversationScenarioSummary],
    dependencies=[Depends(require_user)],
)
def list_conversation_scenarios(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> list[ConversationScenarioSummary]:
    """
    Retrieve **all** conversation scenarios for the current user with summary data.
    Admins receive every scenario in the system.
    """
    return service.list_scenarios_summary(user_profile)


@router.get(
    '/{scenario_id}',
    response_model=ConversationScenarioSummary,
    dependencies=[Depends(require_user)],
)
def get_conversation_scenario_metadata(
    scenario_id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> ConversationScenarioSummary:
    """
    Retrieve detailed metadata for a single conversation scenario.
    """
    return service.get_scenario_summary(scenario_id, user_profile)


@router.post(
    '', response_model=ConversationScenarioCreateResponse, dependencies=[Depends(require_user)]
)
def create_conversation_scenario_with_preparation(
    conversation_scenario: ConversationScenarioCreate,
    background_tasks: BackgroundTasks,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> ConversationScenarioCreateResponse:
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
