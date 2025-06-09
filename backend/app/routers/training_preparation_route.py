from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.conversation_scenario import ConversationScenario
from app.models.training_preparation import (
    TrainingPreparation,
    TrainingPreparationCreate,
    TrainingPreparationRead,
    TrainingPreparationStatus,
)

router = APIRouter(prefix='/training-preparations', tags=['Training Preparations'])


@router.get('/', response_model=list[TrainingPreparationRead])
def get_training_preparations(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[TrainingPreparation]:
    """
    Retrieve all training preparations.
    """
    statement = select(TrainingPreparation)
    preparations = db_session.exec(statement).all()
    return list(preparations)


@router.get('/{preparation_id}', response_model=TrainingPreparationRead)
def get_training_preparation(
    preparation_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> TrainingPreparation:
    """
    Retrieve a specific training preparation by ID.
    """
    preparation = db_session.get(TrainingPreparation, preparation_id)

    if not preparation:
        raise HTTPException(status_code=404, detail='Session preparation not found')

    if preparation.status == TrainingPreparationStatus.pending:
        raise HTTPException(status_code=202, detail='Session preparation in progress.')

    elif preparation.status == TrainingPreparationStatus.failed:
        raise HTTPException(status_code=500, detail='Session preparation failed.')

    return preparation


@router.post('/', response_model=TrainingPreparationRead)
def create_training_preparation(
    preparation: TrainingPreparationCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> TrainingPreparation:
    """
    Create a new training preparation.
    """
    # Validate foreign key
    conversation_scenario = db_session.get(ConversationScenario, preparation.scenario_id)
    if not conversation_scenario:
        raise HTTPException(status_code=404, detail='Conversation scenario not found')

    db_preparation = TrainingPreparation(**preparation.dict())
    db_session.add(db_preparation)
    db_session.commit()
    db_session.refresh(db_preparation)
    return db_preparation


@router.put('/{preparation_id}', response_model=TrainingPreparationRead)
def update_training_preparation(
    preparation_id: UUID,
    updated_data: TrainingPreparationCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> TrainingPreparation:
    """
    Update an existing training preparation.
    """
    preparation = db_session.get(TrainingPreparation, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail='Training preparation not found')

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
def delete_training_preparation(
    preparation_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a training preparation.
    """
    preparation = db_session.get(TrainingPreparation, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail='Training preparation not found')

    db_session.delete(preparation)
    db_session.commit()
    return {'message': 'Training preparation deleted successfully'}
