from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.training_case_model import TrainingCaseModel
from ..models.training_preparation_model import (
    TrainingPreparationCreate,
    TrainingPreparationModel,
    TrainingPreparationRead,
)

router = APIRouter(prefix="/training-preparations", tags=["Training Preparations"])


@router.get("/", response_model=List[TrainingPreparationRead])
def get_training_preparations(
    session: Annotated[Session, Depends(get_session)]
) -> List[TrainingPreparationRead]:
    """
    Retrieve all training preparations.
    """
    statement = select(TrainingPreparationModel)
    preparations = session.exec(statement).all()
    return preparations


@router.post("/", response_model=TrainingPreparationRead)
def create_training_preparation(
    preparation: TrainingPreparationCreate, session: Annotated[Session, Depends(get_session)]
) -> TrainingPreparationModel:
    """
    Create a new training preparation.
    """
    # Validate foreign key
    case = session.get(TrainingCaseModel, preparation.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Training case not found")

    db_preparation = TrainingPreparationModel(**preparation.dict())
    session.add(db_preparation)
    session.commit()
    session.refresh(db_preparation)
    return db_preparation


@router.put("/{preparation_id}", response_model=TrainingPreparationRead)
def update_training_preparation(
    preparation_id: UUID,
    updated_data: TrainingPreparationCreate,
    session: Annotated[Session, Depends(get_session)],
) -> TrainingPreparationModel:
    """
    Update an existing training preparation.
    """
    preparation = session.get(TrainingPreparationModel, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail="Training preparation not found")

    # Validate foreign key
    if updated_data.case_id:
        case = session.get(TrainingCaseModel, updated_data.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Training case not found")

    for key, value in updated_data.dict().items():
        setattr(preparation, key, value)

    session.add(preparation)
    session.commit()
    session.refresh(preparation)
    return preparation


@router.delete("/{preparation_id}", response_model=dict)
def delete_training_preparation(
    preparation_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a training preparation.
    """
    preparation = session.get(TrainingPreparationModel, preparation_id)
    if not preparation:
        raise HTTPException(status_code=404, detail="Training preparation not found")

    session.delete(preparation)
    session.commit()
    return {"message": "Training preparation deleted successfully"}