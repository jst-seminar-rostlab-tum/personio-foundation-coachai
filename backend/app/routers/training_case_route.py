from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.conversation_category import ConversationCategory
from app.models.training_case import (
    TrainingCase,
    TrainingCaseCreate,
    TrainingCaseRead,
)
from app.models.training_preparation import TrainingPreparation, TrainingPreparationRead

router = APIRouter(prefix='/training-case', tags=['Training Cases'])


@router.get('/', response_model=list[TrainingCaseRead])
def get_training_cases(
    session: Annotated[Session, Depends(get_session)],
) -> list[TrainingCase]:
    """
    Retrieve all training cases.
    """
    statement = select(TrainingCase)
    training_cases = session.exec(statement).all()
    return list(training_cases)


# needed
@router.post('/', response_model=TrainingCaseRead)
def create_training_case(
    training_case: TrainingCaseCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingCase:
    """
    Create a new training case.
    """
    # Validate foreign keys
    if training_case.category_id:
        category = session.get(ConversationCategory, training_case.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    db_training_case = TrainingCase(**training_case.dict())
    session.add(db_training_case)
    session.commit()
    session.refresh(db_training_case)
    return db_training_case


@router.put('/{case_id}', response_model=TrainingCaseRead)
def update_training_case(
    case_id: UUID,
    updated_data: TrainingCaseCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingCase:
    """
    Update an existing training case.
    """
    training_case = session.get(TrainingCase, case_id)
    if not training_case:
        raise HTTPException(status_code=404, detail='Training case not found')

    # Validate foreign keys
    if updated_data.category_id:
        category = session.get(ConversationCategory, updated_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    for key, value in updated_data.dict().items():
        setattr(training_case, key, value)

    session.add(training_case)
    session.commit()
    session.refresh(training_case)
    return training_case


@router.delete('/{case_id}', response_model=dict)
def delete_training_case(case_id: UUID, session: Annotated[Session, Depends(get_session)]) -> dict:
    """
    Delete a training case.
    """
    training_case = session.get(TrainingCase, case_id)
    if not training_case:
        raise HTTPException(status_code=404, detail='Training case not found')

    session.delete(training_case)
    session.commit()
    return {'message': 'Training case deleted successfully'}


@router.get('/{id_training_case}/preparation', response_model=TrainingPreparationRead)
def get_training_preparation_by_case_id(
    id_training_case: UUID, session: Annotated[Session, Depends(get_session)]
) -> TrainingPreparation:
    """
    Retrieve the training preparation data for a given training case ID.
    """
    # Validate that the training case exists
    training_case = session.get(TrainingCase, id_training_case)
    if not training_case:
        raise HTTPException(status_code=404, detail='Training case not found')

    # Fetch the associated training preparation
    statement = select(TrainingPreparation).where(TrainingPreparation.case_id == id_training_case)
    training_preparation = session.exec(statement).first()

    if not training_preparation:
        raise HTTPException(status_code=404, detail='Training preparation not found')

    return training_preparation
