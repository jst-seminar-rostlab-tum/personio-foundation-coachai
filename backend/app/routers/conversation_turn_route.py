from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_session
from app.models.conversation_turn import (
    ConversationTurn,
    ConversationTurnCreate,
    ConversationTurnRead,
)
from app.models.training_session import TrainingSession

router = APIRouter(prefix='/conversation-turns', tags=['Conversation Turns'])


@router.get('/', response_model=list[ConversationTurnRead])
def get_conversation_turns(
    db_session: Annotated[DBSession, Depends(get_session)],
) -> list[ConversationTurn]:
    """
    Retrieve all conversation turns.
    """
    statement = select(ConversationTurn)
    turns = db_session.exec(statement).all()
    return list(turns)


@router.post('/', response_model=ConversationTurnRead)
def create_conversation_turn(
    turn: ConversationTurnCreate, db_session: Annotated[DBSession, Depends(get_session)]
) -> ConversationTurn:
    """
    Create a new conversation turn.
    """
    # Validate foreign key
    training_session = db_session.get(TrainingSession, turn.session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    db_turn = ConversationTurn(**turn.dict())
    db_session.add(db_turn)
    db_session.commit()
    db_session.refresh(db_turn)
    return db_turn


@router.put('/{turn_id}', response_model=ConversationTurnRead)
def update_conversation_turn(
    turn_id: UUID,
    updated_data: ConversationTurnCreate,
    db_session: Annotated[DBSession, Depends(get_session)],
) -> ConversationTurn:
    """
    Update an existing conversation turn.
    """
    turn = db_session.get(ConversationTurn, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail='Conversation turn not found')

    # Validate foreign key
    if updated_data.session_id:
        training_session = db_session.get(TrainingSession, updated_data.session_id)
        if not training_session:
            raise HTTPException(status_code=404, detail='Training session not found')

    for key, value in updated_data.dict().items():
        setattr(turn, key, value)

    db_session.add(turn)
    db_session.commit()
    db_session.refresh(turn)
    return turn


@router.delete('/{turn_id}', response_model=dict)
def delete_conversation_turn(
    turn_id: UUID, db_session: Annotated[DBSession, Depends(get_session)]
) -> dict:
    """
    Delete a conversation turn.
    """
    turn = db_session.get(ConversationTurn, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail='Conversation turn not found')

    db_session.delete(turn)
    db_session.commit()
    return {'message': 'Conversation turn deleted successfully'}
