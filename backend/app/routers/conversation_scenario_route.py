from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlmodel import Session as DBSession

from app.dependencies.auth import require_user
from app.dependencies.database import get_db_session
from app.models.user_profile import UserProfile
from app.schemas.conversation_scenario import (
    ConversationScenarioConfirm,
    ConversationScenarioCreate,
    ConversationScenarioReadDetail,
    PaginatedConversationScenarioSummary,
)
from app.schemas.scenario_preparation import ScenarioPreparationRead
from app.services.conversation_scenario_service import ConversationScenarioService

router = APIRouter(prefix='/conversation-scenarios', tags=['Conversation Scenarios'])


def get_conversation_scenario_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ConversationScenarioService:
    """
    Dependency factory to inject the ConversationScenarioService.
    """
    return ConversationScenarioService(db_session)


@router.get(
    '',  # /conversation-scenarios
    response_model=PaginatedConversationScenarioSummary,
    dependencies=[Depends(require_user)],
)
def list_conversation_scenarios(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> PaginatedConversationScenarioSummary:
    """
    Retrieve **all** conversation scenarios for the current user with summary data.
    Admins receive every scenario in the system.
    """
    return service.list_scenarios_summary(user_profile, page, page_size)


@router.get(
    '/{id}',
    response_model=ConversationScenarioReadDetail,
    dependencies=[Depends(require_user)],
)
def get_conversation_scenario_metadata(
    id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> ConversationScenarioReadDetail:
    """
    Retrieve detailed metadata for a single conversation scenario.
    """
    return service.get_scenario_summary(id, user_profile)


@router.post('', response_model=ConversationScenarioConfirm, dependencies=[Depends(require_user)])
def create_conversation_scenario_with_preparation(
    conversation_scenario: ConversationScenarioCreate,
    background_tasks: BackgroundTasks,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
    custom_scenario: bool = False,
    advised_scenario: bool = False,
) -> ConversationScenarioConfirm:
    """
    Create a new conversation scenario and start the preparation process in the background.
    """
    return service.create_conversation_scenario_with_preparation(
        conversation_scenario, user_profile, background_tasks, custom_scenario, advised_scenario
    )


@router.get('/{id}/preparation', response_model=ScenarioPreparationRead)
def get_scenario_preparation_by_scenario_id(
    id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> ScenarioPreparationRead:
    """
    Retrieve the scenario preparation data for a given conversation scenario ID.
    """
    return service.get_scenario_preparation_by_scenario_id(id, user_profile)


@router.delete('/clear-all', response_model=dict)
def clear_all_conversation_scenarios(
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> dict:
    """
    Deletes all conversation scenarios for the authenticated user.
    """
    return service.clear_all_conversation_scenarios(user_profile)


@router.delete('/{id}', response_model=dict)
def delete_conversation_scenario(
    id: UUID,
    user_profile: Annotated[UserProfile, Depends(require_user)],
    service: Annotated[ConversationScenarioService, Depends(get_conversation_scenario_service)],
) -> dict:
    """
    Deletes a single conversation scenario by ID.
    """
    return service.delete_conversation_scenario(id, user_profile)
