from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models.user_confidence_score import (
    UserConfidenceScore,
    UserConfidenceScoreCreate,
    UserConfidenceScoreRead,
)

router = APIRouter(prefix='/user-confidence-scores', tags=['User Confidence Scores'])


@router.get('/', response_model=list[UserConfidenceScoreRead])
def get_user_confidence_scores(
    db_session: Annotated[DBSession, Depends(get_session)],
) -> list[UserConfidenceScore]:
    """
    Retrieve all user confidence scores.
    """
    statement = select(UserConfidenceScore)
    results = db_session.exec(statement).all()
    return list(results)


@router.post('/', response_model=UserConfidenceScoreRead)
def create_user_confidence_score(
    user_confidence_score: UserConfidenceScoreCreate,
    db_session: Annotated[DBSession, Depends(get_session)],
) -> UserConfidenceScore:
    """
    Create a new user confidence score.
    """
    new_score = UserConfidenceScore(**user_confidence_score.dict())
    db_session.add(new_score)
    db_session.commit()
    db_session.refresh(new_score)
    return new_score


@router.put('/{score_id}', response_model=UserConfidenceScoreRead)
def update_user_confidence_score(
    score_id: UUID,
    updated_data: UserConfidenceScoreCreate,
    db_session: Annotated[DBSession, Depends(get_session)],
) -> UserConfidenceScore:
    """
    Update an existing user confidence score.
    """
    score = db_session.get(UserConfidenceScore, score_id)
    if not score:
        raise HTTPException(status_code=404, detail='User confidence score not found')
    for key, value in updated_data.dict().items():
        setattr(score, key, value)
    db_session.add(score)
    db_session.commit()
    db_session.refresh(score)
    return score


@router.delete('/{score_id}', response_model=dict)
def delete_user_confidence_score(
    score_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> dict:
    """
    Delete a user confidence score.
    """
    score = db_session.get(UserConfidenceScore, score_id)
    if not score:
        raise HTTPException(status_code=404, detail='User confidence score not found')
    db_session.delete(score)
    db_session.commit()
    return {'message': 'User confidence score deleted successfully'}
