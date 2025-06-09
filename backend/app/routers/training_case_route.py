from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_db_session
from app.models.conversation_category import ConversationCategory
from app.models.training_case import (
    TrainingCase,
    TrainingCaseCreate,
    TrainingCaseRead,
)
from app.models.training_preparation import TrainingPreparation, TrainingPreparationRead
from app.schemas.training_preparation_schema import TrainingPreparationRequest
from app.services.training_case_service import create_training_case
from app.services.training_preparation_service import (
    create_pending_preparation,
    generate_training_preparation,
)

router = APIRouter(prefix='/training-case', tags=['Training Cases'])


@router.get('/', response_model=list[TrainingCaseRead])
def get_training_cases(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[TrainingCase]:
    """
    Retrieve all training cases.
    """
    statement = select(TrainingCase)
    training_cases = db_session.exec(statement).all()
    return list(training_cases)


@router.post('/', response_model=TrainingCaseRead)
def create_training_case_with_preparation(
    training_case: TrainingCaseCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    """
    Create a new training case and start the preparation process in the background.
    """
    category = None
    # 1. Validate foreign keys
    if training_case.category_id:
        category = db_session.get(ConversationCategory, training_case.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    # 2. Create new TrainingCase
    training_case = create_training_case(training_case, db_session)

    # 3. Initialize preparation（status = pending）
    prep = create_pending_preparation(training_case.id, db_session)

    preparation_request = TrainingPreparationRequest(
        category=category.name,
        context=training_case.context,
        goal=training_case.goal,
        other_party=training_case.other_party,
        num_objectives=3,  # Example value, adjust as needed
        num_checkpoints=3,  # Example value, adjust as needed
    )

    # 4. Start background task to generate preparation
    background_tasks.add_task(
        generate_training_preparation, prep.id, preparation_request, get_db_session
    )
    # 5. Return response
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            'message': 'Training case created, preparation started.',
            'case_id': str(training_case.id),
        },
    )


@router.put('/{case_id}', response_model=TrainingCaseRead)
def update_training_case(
    case_id: UUID,
    updated_data: TrainingCaseCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> TrainingCase:
    """
    Update an existing training case.
    """
    training_case = db_session.get(TrainingCase, case_id)
    if not training_case:
        raise HTTPException(status_code=404, detail='Training case not found')

    # Validate foreign keys
    if updated_data.category_id:
        category = db_session.get(ConversationCategory, updated_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    for key, value in updated_data.dict().items():
        setattr(training_case, key, value)

    db_session.add(training_case)
    db_session.commit()
    db_session.refresh(training_case)
    return training_case


@router.delete('/{case_id}', response_model=dict)
def delete_training_case(
    case_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a training case.
    """
    training_case = db_session.get(TrainingCase, case_id)
    if not training_case:
        raise HTTPException(status_code=404, detail='Training case not found')

    db_session.delete(training_case)
    db_session.commit()
    return {'message': 'Training case deleted successfully'}


@router.get('/{id_training_case}/preparation', response_model=TrainingPreparationRead)
def get_training_preparation_by_case_id(
    id_training_case: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> TrainingPreparation:
    """
    Retrieve the training preparation data for a given training case ID.
    """
    # Validate that the training case exists
    training_case = db_session.get(TrainingCase, id_training_case)
    if not training_case:
        raise HTTPException(status_code=404, detail='Training case not found')

    # Fetch the associated training preparation
    statement = select(TrainingPreparation).where(TrainingPreparation.case_id == id_training_case)
    training_preparation = db_session.exec(statement).first()

    if not training_preparation:
        raise HTTPException(status_code=404, detail='Training preparation not found')

    return training_preparation
