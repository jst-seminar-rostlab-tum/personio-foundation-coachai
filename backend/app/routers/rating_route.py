from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.rating import Rating, RatingCreate, RatingRead
from app.models.session import Session

router = APIRouter(prefix='/ratings', tags=['Ratings'])


@router.get('/', response_model=list[RatingRead])
def get_ratings(db_session: Annotated[DBSession, Depends(get_db_session)]) -> list[Rating]:
    """
    Retrieve all ratings.
    """
    statement = select(Rating)
    ratings = db_session.exec(statement).all()
    return list(ratings)


@router.post('/', response_model=RatingRead)
def create_rating(
    rating: RatingCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> Rating:
    """
    Create a new rating.
    """
    # Validate foreign key
    session = db_session.get(Session, rating.session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    db_rating = Rating(**rating.dict())
    db_session.add(db_rating)
    db_session.commit()
    db_session.refresh(db_rating)
    return db_rating


@router.put('/{rating_id}', response_model=RatingRead)
def update_rating(
    rating_id: UUID,
    updated_data: RatingCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> Rating:
    """
    Update an existing rating.
    """
    rating = db_session.get(Rating, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail='Rating not found')

    # Validate foreign key
    if updated_data.session_id:
        session = db_session.get(Session, updated_data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail='Session not found')

    for key, value in updated_data.dict().items():
        setattr(rating, key, value)

    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return rating


@router.delete('/{rating_id}', response_model=dict)
def delete_rating(
    rating_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a rating.
    """
    rating = db_session.get(Rating, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail='Rating not found')

    db_session.delete(rating)
    db_session.commit()
    return {'message': 'Rating deleted successfully'}
