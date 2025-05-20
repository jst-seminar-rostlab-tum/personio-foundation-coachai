from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Annotated
from uuid import UUID

from ..database import get_session
from ..models.rating_model import RatingModel, RatingCreate, RatingRead
from ..models.training_session_model import TrainingSessionModel

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.get("/", response_model=List[RatingRead])
def get_ratings(
    session: Annotated[Session, Depends(get_session)]
) -> List[RatingRead]:
    """
    Retrieve all ratings.
    """
    statement = select(RatingModel)
    ratings = session.exec(statement).all()
    return ratings


@router.post("/", response_model=RatingRead)
def create_rating(
    rating: RatingCreate, session: Annotated[Session, Depends(get_session)]
) -> RatingModel:
    """
    Create a new rating.
    """
    # Validate foreign key
    training_session = session.get(TrainingSessionModel, rating.session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail="Training session not found")

    db_rating = RatingModel(**rating.dict())
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating


@router.put("/{rating_id}", response_model=RatingRead)
def update_rating(
    rating_id: UUID,
    updated_data: RatingCreate,
    session: Annotated[Session, Depends(get_session)],
) -> RatingModel:
    """
    Update an existing rating.
    """
    rating = session.get(RatingModel, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    # Validate foreign key
    if updated_data.session_id:
        training_session = session.get(TrainingSessionModel, updated_data.session_id)
        if not training_session:
            raise HTTPException(status_code=404, detail="Training session not found")

    for key, value in updated_data.dict().items():
        setattr(rating, key, value)

    session.add(rating)
    session.commit()
    session.refresh(rating)
    return rating


@router.delete("/{rating_id}", response_model=dict)
def delete_rating(
    rating_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a rating.
    """
    rating = session.get(RatingModel, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    session.delete(rating)
    session.commit()
    return {"message": "Rating deleted successfully"}