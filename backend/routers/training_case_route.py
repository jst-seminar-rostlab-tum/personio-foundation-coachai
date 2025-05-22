from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.conversation_category import ConversationCategory
from ..models.scenario_template import ScenarioTemplate
from ..models.training_case import (
    TrainingCaseCreate,
    TrainingCase,
    TrainingCaseRead,
)

router = APIRouter(prefix="/training-cases", tags=["Training Cases"])


@router.get("/", response_model=List[TrainingCaseRead])
def get_training_cases(
    session: Annotated[Session, Depends(get_session)]
) -> List[TrainingCaseRead]:
    """
    Retrieve all training cases.
    """
    statement = select(TrainingCase)
    training_cases = session.exec(statement).all()
    return training_cases


@router.post("/", response_model=TrainingCaseRead)
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
            raise HTTPException(status_code=404, detail="Category not found")

    if training_case.scenario_template_id:
        template = session.get(ScenarioTemplate, training_case.scenario_template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Scenario template not found")

    db_training_case = TrainingCase(**training_case.dict())
    session.add(db_training_case)
    session.commit()
    session.refresh(db_training_case)
    return db_training_case


@router.put("/{case_id}", response_model=TrainingCaseRead)
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
        raise HTTPException(status_code=404, detail="Training case not found")

    # Validate foreign keys
    if updated_data.category_id:
        category = session.get(ConversationCategory, updated_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    if updated_data.scenario_template_id:
        template = session.get(ScenarioTemplate, updated_data.scenario_template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Scenario template not found")

    for key, value in updated_data.dict().items():
        setattr(training_case, key, value)

    session.add(training_case)
    session.commit()
    session.refresh(training_case)
    return training_case


@router.delete("/{case_id}", response_model=dict)
def delete_training_case(
    case_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a training case.
    """
    training_case = session.get(TrainingCase, case_id)
    if not training_case:
        raise HTTPException(status_code=404, detail="Training case not found")

    session.delete(training_case)
    session.commit()
    return {"message": "Training case deleted successfully"}