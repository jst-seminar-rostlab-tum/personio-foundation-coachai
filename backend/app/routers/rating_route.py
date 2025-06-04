from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.rating import Rating, RatingCreate, RatingRead
from app.models.training_session import TrainingSession

router = APIRouter(prefix='/ratings', tags=['Ratings'])


@router.get('/', response_model=list[RatingRead])
def get_ratings(session: Annotated[Session, Depends(get_session)]) -> list[Rating]:
    """
    Retrieve all ratings.
    """
    statement = select(Rating)
    ratings = session.exec(statement).all()
    return list(ratings)


@router.post('/', response_model=RatingRead)
def create_rating(
    rating: RatingCreate, session: Annotated[Session, Depends(get_session)]
) -> Rating:
    """
    Create a new rating.
    """
    # Validate foreign key
    training_session = session.get(TrainingSession, rating.session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    db_rating = Rating(**rating.dict())
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating


@router.put('/{rating_id}', response_model=RatingRead)
def update_rating(
    rating_id: UUID,
    updated_data: RatingCreate,
    session: Annotated[Session, Depends(get_session)],
) -> Rating:
    """
    Update an existing rating.
    """
    rating = session.get(Rating, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail='Rating not found')

    # Validate foreign key
    if updated_data.session_id:
        training_session = session.get(TrainingSession, updated_data.session_id)
        if not training_session:
            raise HTTPException(status_code=404, detail='Training session not found')

    for key, value in updated_data.dict().items():
        setattr(rating, key, value)

    session.add(rating)
    session.commit()
    session.refresh(rating)
    return rating


@router.delete('/{rating_id}', response_model=dict)
def delete_rating(rating_id: UUID, session: Annotated[Session, Depends(get_session)]) -> dict:
    """
    Delete a rating.
    """
    rating = session.get(Rating, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail='Rating not found')

    session.delete(rating)
    session.commit()
    return {'message': 'Rating deleted successfully'}
