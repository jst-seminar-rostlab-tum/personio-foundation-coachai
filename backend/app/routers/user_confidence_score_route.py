from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.user_confidence_score import (
    UserConfidenceScore,
    UserConfidenceScoreCreate,
    UserConfidenceScoreRead,
)

router = APIRouter(prefix='/user-confidence-scores', tags=['User Confidence Scores'])


@router.get('/', response_model=list[UserConfidenceScoreRead])
def get_user_confidence_scores(
    session: Annotated[Session, Depends(get_session)],
) -> list[UserConfidenceScore]:
    """
    Retrieve all user confidence scores.
    """
    statement = select(UserConfidenceScore)
    results = session.exec(statement).all()
    return list(results)


@router.post('/', response_model=UserConfidenceScoreRead)
def create_user_confidence_score(
    user_confidence_score: UserConfidenceScoreCreate,
    session: Annotated[Session, Depends(get_session)],
) -> UserConfidenceScore:
    """
    Create a new user confidence score.
    """
    new_score = UserConfidenceScore(**user_confidence_score.dict())
    session.add(new_score)
    session.commit()
    session.refresh(new_score)
    return new_score


@router.put('/{score_id}', response_model=UserConfidenceScoreRead)
def update_user_confidence_score(
    score_id: UUID,
    updated_data: UserConfidenceScoreCreate,
    session: Annotated[Session, Depends(get_session)],
) -> UserConfidenceScore:
    """
    Update an existing user confidence score.
    """
    score = session.get(UserConfidenceScore, score_id)
    if not score:
        raise HTTPException(status_code=404, detail='User confidence score not found')
    for key, value in updated_data.dict().items():
        setattr(score, key, value)
    session.add(score)
    session.commit()
    session.refresh(score)
    return score


@router.delete('/{score_id}', response_model=dict)
def delete_user_confidence_score(
    score_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a user confidence score.
    """
    score = session.get(UserConfidenceScore, score_id)
    if not score:
        raise HTTPException(status_code=404, detail='User confidence score not found')
    session.delete(score)
    session.commit()
    return {'message': 'User confidence score deleted successfully'}
