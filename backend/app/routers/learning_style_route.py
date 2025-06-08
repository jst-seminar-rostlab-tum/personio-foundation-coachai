from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models.learning_style import LearningStyle, LearningStyleCreate, LearningStyleRead

router = APIRouter(prefix='/learning-styles', tags=['Learning Styles'])


@router.get('/', response_model=list[LearningStyleRead])
def get_learning_styles(
    db_session: Annotated[DBSession, Depends(get_session)],
) -> list[LearningStyle]:
    """
    Retrieve all learning styles.
    """
    statement = select(LearningStyle)
    results = db_session.exec(statement).all()
    return list(results)


@router.post('/', response_model=LearningStyleRead)
def create_learning_style(
    learning_style: LearningStyleCreate, db_session: Annotated[DBSession, Depends(get_session)]
) -> LearningStyle:
    """
    Create a new learning style.
    """
    new_learning_style = LearningStyle(**learning_style.dict())
    db_session.add(new_learning_style)
    db_session.commit()
    db_session.refresh(new_learning_style)
    return new_learning_style


@router.put('/{learning_style_id}', response_model=LearningStyleRead)
def update_learning_style(
    learning_style_id: UUID,
    updated_data: LearningStyleCreate,
    db_session: Annotated[DBSession, Depends(get_session)],
) -> LearningStyle:
    """
    Update an existing learning style.
    """
    learning_style = db_session.get(LearningStyle, learning_style_id)
    if not learning_style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    for key, value in updated_data.dict().items():
        setattr(learning_style, key, value)
    db_session.add(learning_style)
    db_session.commit()
    db_session.refresh(learning_style)
    return learning_style


@router.delete('/{learning_style_id}', response_model=dict)
def delete_learning_style(
    learning_style_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> dict:
    """
    Delete a learning style.
    """
    learning_style = db_session.get(LearningStyle, learning_style_id)
    if not learning_style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    db_session.delete(learning_style)
    db_session.commit()
    return {'message': 'Learning style deleted successfully'}
