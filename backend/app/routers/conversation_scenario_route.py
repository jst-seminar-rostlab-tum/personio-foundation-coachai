from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_db_session
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioCreate,
    ConversationScenarioRead,
)
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationRead
from app.schemas.scenario_preparation_schema import ScenarioPreparationRequest
from app.services.scenario_preparation_service import (
    create_pending_preparation,
    generate_scenario_preparation,
)

router = APIRouter(prefix='/conversation-scenario', tags=['Conversation Scenarios'])


@router.get('/', response_model=list[ConversationScenarioRead])
def get_conversation_scenarios(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[ConversationScenario]:
    """
    Retrieve all conversation scenarios.
    """
    statement = select(ConversationScenario)
    conversation_scenarios = db_session.exec(statement).all()
    return list(conversation_scenarios)


@router.post('/', response_model=ConversationScenarioRead)
def create_conversation_scenario_with_preparation(
    conversation_scenario: ConversationScenarioCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
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

    # 2. Create new ConversationScenario
    new_conversation_scenario = ConversationScenario(**conversation_scenario.model_dump())
    db_session.add(new_conversation_scenario)
    db_session.commit()
    db_session.refresh(new_conversation_scenario)

    # 3. Initialize preparation（status = pending）
    prep = create_pending_preparation(new_conversation_scenario.id, db_session)

    preparation_request = ScenarioPreparationRequest(
        category=category.name,
        context=new_conversation_scenario.context,
        goal=new_conversation_scenario.goal,
        other_party=new_conversation_scenario.other_party,
        num_objectives=3,  # Example value, adjust as needed
        num_checkpoints=3,  # Example value, adjust as needed
    )

    # 4. Start background task to generate preparation
    background_tasks.add_task(
        generate_scenario_preparation, prep.id, preparation_request, get_db_session
    )
    # 5. Return response
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            'message': 'Conversation scenario created, preparation started.',
            'scenario_id': str(new_conversation_scenario.id),
        },
    )


@router.put('/{scenario_id}', response_model=ConversationScenarioRead)
def update_conversation_scenario(
    scenario_id: UUID,
    updated_data: ConversationScenarioCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ConversationScenario:
    """
    Update an existing conversation scenario.
    """
    conversation_scenario = db_session.get(ConversationScenario, scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    # Validate foreign keys
    if updated_data.category_id:
        category = db_session.get(ConversationCategory, updated_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    for key, value in updated_data.dict().items():
        setattr(conversation_scenario, key, value)

    db_session.add(conversation_scenario)
    db_session.commit()
    db_session.refresh(conversation_scenario)
    return conversation_scenario


@router.delete('/{scenario_id}', response_model=dict)
def delete_conversation_scenario(
    scenario_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a conversation scenario.
    """
    conversation_scenario = db_session.get(ConversationScenario, scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    db_session.delete(conversation_scenario)
    db_session.commit()
    return {'message': 'Conversation scenario deleted successfully'}


@router.get('/{scenario_id}/preparation', response_model=ScenarioPreparationRead)
def get_scenario_preparation_by_scenario_id(
    scenario_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> ScenarioPreparation:
    """
    Retrieve the scenario preparation data for a given conversation scenario ID.
    """
    # Validate that the conversation scenario exists
    conversation_scenario = db_session.get(ConversationScenario, scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    # Fetch the associated scenario preparation
    statement = select(ScenarioPreparation).where(ScenarioPreparation.scenario_id == scenario_id)
    scenario_preparation = db_session.exec(statement).first()

    if not scenario_preparation:
        raise HTTPException(status_code=404, detail='Scenario preparation not found')

    return scenario_preparation
