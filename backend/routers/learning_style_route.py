from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.learning_style import LearningStyle, LearningStyleCreate, LearningStyleRead

router = APIRouter(prefix='/learning-styles', tags=['Learning Styles'])


@router.get('/', response_model=list[LearningStyleRead])
def get_learning_styles(session: Annotated[Session, Depends(get_session)]) -> list[LearningStyle]:
    """
    Retrieve all learning styles.
    """
    statement = select(LearningStyle)
    results = session.exec(statement).all()
    return list(results)


@router.post('/', response_model=LearningStyleRead)
def create_learning_style(
    learning_style: LearningStyleCreate, session: Annotated[Session, Depends(get_session)]
) -> LearningStyle:
    """
    Create a new learning style.
    """
    new_learning_style = LearningStyle(**learning_style.dict())
    session.add(new_learning_style)
    session.commit()
    session.refresh(new_learning_style)
    return new_learning_style


@router.put('/{learning_style_id}', response_model=LearningStyleRead)
def update_learning_style(
    learning_style_id: UUID,
    updated_data: LearningStyleCreate,
    session: Annotated[Session, Depends(get_session)],
) -> LearningStyle:
    """
    Update an existing learning style.
    """
    learning_style = session.get(LearningStyle, learning_style_id)
    if not learning_style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    for key, value in updated_data.dict().items():
        setattr(learning_style, key, value)
    session.add(learning_style)
    session.commit()
    session.refresh(learning_style)
    return learning_style


@router.delete('/{learning_style_id}', response_model=dict)
def delete_learning_style(
    learning_style_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a learning style.
    """
    learning_style = session.get(LearningStyle, learning_style_id)
    if not learning_style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    session.delete(learning_style)
    session.commit()
    return {'message': 'Learning style deleted successfully'}
