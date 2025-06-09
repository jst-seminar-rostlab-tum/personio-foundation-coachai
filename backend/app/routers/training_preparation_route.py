from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.conversation_scenario import ConversationScenario
from app.models.training_preparation import (
    ScenarioPreparation,
    ScenarioPreparationCreate,
    ScenarioPreparationRead,
    ScenarioPreparationStatus,
)

router = APIRouter(prefix='/scenario-preparation', tags=['Scenario Preparations'])


@router.get('/', response_model=list[ScenarioPreparationRead])
def get_scenario_preparations(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[ScenarioPreparation]:
    """
    Retrieve all scenario preparations.
    """
    statement = select(ScenarioPreparation)
    preparations = db_session.exec(statement).all()
    return list(preparations)


@router.get('/{preparation_id}', response_model=ScenarioPreparationRead)
def get_scenario_preparation(
    preparation_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> ScenarioPreparation:
    """
    Retrieve a specific scenario preparation by ID.
    """
    preparation = db_session.get(ScenarioPreparation, preparation_id)

    if not preparation:
        raise HTTPException(status_code=404, detail='Session preparation not found')

    if preparation.status == ScenarioPreparationStatus.pending:
        raise HTTPException(status_code=202, detail='Session preparation in progress.')

    elif preparation.status == ScenarioPreparationStatus.failed:
        raise HTTPException(status_code=500, detail='Session preparation failed.')

    return preparation


@router.post('/', response_model=ScenarioPreparationRead)
def create_scenario_preparation(
    preparation: ScenarioPreparationCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ScenarioPreparation:
    """
    Create a new scenario preparation.
    """
    # Validate foreign key
    conversation_scenario = db_session.get(ConversationScenario, preparation.scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    new_preparation = ScenarioPreparation(**preparation.dict())
    db_session.add(new_preparation)
    db_session.commit()
    db_session.refresh(new_preparation)
    return new_preparation


@router.put('/{preparation_id}', response_model=ScenarioPreparationRead)
def update_scenario_preparation(
    preparation_id: UUID,
    updated_data: ScenarioPreparationCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ScenarioPreparation:
    """
    Update an existing scenario preparation.
    """
    preparation = db_session.get(ScenarioPreparation, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail='Scenario preparation not found')

    # Validate foreign key
    if updated_data.scenario_id:
        conversation_scenario = db_session.get(ConversationScenario, updated_data.scenario_id)
        if not conversation_scenario:
            raise HTTPException(status_code=404, detail='Conversation scenario not found')

    for key, value in updated_data.dict().items():
        setattr(preparation, key, value)

    db_session.add(preparation)
    db_session.commit()
    db_session.refresh(preparation)
    return preparation


@router.delete('/{preparation_id}', response_model=dict)
def delete_scenario_preparation(
    preparation_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a scenario preparation.
    """
    preparation = db_session.get(ScenarioPreparation, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail='Scenario preparation not found')

    db_session.delete(preparation)
    db_session.commit()
    return {'message': 'Scenario preparation deleted successfully'}
