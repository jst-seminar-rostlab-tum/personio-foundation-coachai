from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import MessageModel

router = APIRouter(prefix='/messages', tags=['Messages'])


@router.post('/', response_model=MessageModel)
def create_message(
    message: MessageModel, session: Annotated[Session, Depends(get_session)]
) -> MessageModel:
    """
    Create a new message.
    """
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@router.get('/', response_model=list[MessageModel])
def read_messages(
    session: Annotated[Session, Depends(get_session)], skip: int = 0, limit: int = 100
) -> list[MessageModel]:
    """
    Retrieve a list of messages.
    """
    statement = select(MessageModel).offset(skip).limit(limit)
    messages = session.exec(statement).all()
    return list(messages)
