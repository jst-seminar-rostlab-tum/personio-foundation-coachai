from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.conversation_turn_model import (
    ConversationTurnCreate,
    ConversationTurnModel,
    ConversationTurnRead,
)
from ..models.training_session_model import TrainingSessionModel

router = APIRouter(prefix='/conversation-turns', tags=['Conversation Turns'])


@router.get('/', response_model=list[ConversationTurnRead])
def get_conversation_turns(
    session: Annotated[Session, Depends(get_session)],
) -> list[ConversationTurnModel]:
    """
    Retrieve all conversation turns.
    """
    statement = select(ConversationTurnModel)
    turns = session.exec(statement).all()
    return list(turns)


@router.post('/', response_model=ConversationTurnRead)
def create_conversation_turn(
    turn: ConversationTurnCreate, session: Annotated[Session, Depends(get_session)]
) -> ConversationTurnModel:
    """
    Create a new conversation turn.
    """
    # Validate foreign key
    training_session = session.get(TrainingSessionModel, turn.session_id)
    if not training_session:
        raise HTTPException(status_code=404, detail='Training session not found')

    db_turn = ConversationTurnModel(**turn.dict())
    session.add(db_turn)
    session.commit()
    session.refresh(db_turn)
    return db_turn


@router.put('/{turn_id}', response_model=ConversationTurnRead)
def update_conversation_turn(
    turn_id: UUID,
    updated_data: ConversationTurnCreate,
    session: Annotated[Session, Depends(get_session)],
) -> ConversationTurnModel:
    """
    Update an existing conversation turn.
    """
    turn = session.get(ConversationTurnModel, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail='Conversation turn not found')

    # Validate foreign key
    if updated_data.session_id:
        training_session = session.get(TrainingSessionModel, updated_data.session_id)
        if not training_session:
            raise HTTPException(status_code=404, detail='Training session not found')

    for key, value in updated_data.dict().items():
        setattr(turn, key, value)

    session.add(turn)
    session.commit()
    session.refresh(turn)
    return turn


@router.delete('/{turn_id}', response_model=dict)
def delete_conversation_turn(
    turn_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a conversation turn.
    """
    turn = session.get(ConversationTurnModel, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail='Conversation turn not found')

    session.delete(turn)
    session.commit()
    return {'message': 'Conversation turn deleted successfully'}
