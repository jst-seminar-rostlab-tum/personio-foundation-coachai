from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.training_case import TrainingCase
from app.models.training_preparation import (
    TrainingPreparation,
    TrainingPreparationCreate,
    TrainingPreparationRead,
    TrainingPreparationStatus,
)

router = APIRouter(prefix='/training-preparations', tags=['Training Preparations'])


@router.get('/', response_model=list[TrainingPreparationRead])
def get_training_preparations(
    session: Annotated[Session, Depends(get_session)],
) -> list[TrainingPreparation]:
    """
    Retrieve all training preparations.
    """
    statement = select(TrainingPreparation)
    preparations = session.exec(statement).all()
    return list(preparations)


@router.get('/{preparation_id}', response_model=TrainingPreparationRead)
def get_training_preparation(
    preparation_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> TrainingPreparation:
    """
    Retrieve a specific training preparation by ID.
    """
    preparation = session.get(TrainingPreparation, preparation_id)

    if not preparation:
        raise HTTPException(status_code=404, detail='Session preparation not found')

    if preparation.status == TrainingPreparationStatus.pending:
        raise HTTPException(status_code=202, detail='Session preparation in progress.')

    elif preparation.status == TrainingPreparationStatus.failed:
        raise HTTPException(status_code=500, detail='Session preparation failed.')

    return preparation


@router.post('/', response_model=TrainingPreparationRead)
def create_training_preparation(
    preparation: TrainingPreparationCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingPreparation:
    """
    Create a new training preparation.
    """
    # Validate foreign key
    case = session.get(TrainingCase, preparation.case_id)
    if not case:
        raise HTTPException(status_code=404, detail='Training case not found')

    db_preparation = TrainingPreparation(**preparation.dict())
    session.add(db_preparation)
    session.commit()
    session.refresh(db_preparation)
    return db_preparation


@router.put('/{preparation_id}', response_model=TrainingPreparationRead)
def update_training_preparation(
    preparation_id: UUID,
    updated_data: TrainingPreparationCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingPreparation:
    """
    Update an existing training preparation.
    """
    preparation = session.get(TrainingPreparation, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail='Training preparation not found')

    # Validate foreign key
    if updated_data.case_id:
        case = session.get(TrainingCase, updated_data.case_id)
        if not case:
            raise HTTPException(status_code=404, detail='Training case not found')

    for key, value in updated_data.dict().items():
        setattr(preparation, key, value)

    session.add(preparation)
    session.commit()
    session.refresh(preparation)
    return preparation


@router.delete('/{preparation_id}', response_model=dict)
def delete_training_preparation(
    preparation_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a training preparation.
    """
    preparation = session.get(TrainingPreparation, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail='Training preparation not found')

    session.delete(preparation)
    session.commit()
    return {'message': 'Training preparation deleted successfully'}
