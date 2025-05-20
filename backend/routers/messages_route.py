# from typing import Annotated

# from fastapi import APIRouter, Depends

# from ..database import get_db
# from ..models import MessageModel
# from ..schemas import MessageCreateSchema, MessageSchema

# router = APIRouter(prefix='/messages', tags=['Messages'])


# @router.post('/', response_model=MessageSchema)
# def create_message(
#     message: MessageCreateSchema, db: Annotated[dict, Depends(get_db)]
# ) -> MessageModel:
#     db_message = MessageModel(content=message.content)
#     db.add(db_message)
#     db.commit()
#     db.refresh(db_message)
#     return db_message


# @router.get('/', response_model=list[MessageSchema])
# def read_messages(
#     db: Annotated[dict, Depends(get_db)], skip: int = 0, limit: int = 100
# ) -> list[MessageSchema]:
#     db_messages = db.query(MessageModel).offset(skip).limit(limit).all()
#     messages = [MessageSchema.model_validate(db_message) for db_message in db_messages]
#     return messages
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Annotated

from ..database import get_session
from ..models import MessageModel

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageModel)
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


@router.get("/", response_model=list[MessageModel])
def read_messages(
    session: Annotated[Session, Depends(get_session)], skip: int = 0, limit: int = 100
) -> list[MessageModel]:
    """
    Retrieve a list of messages.
    """
    statement = select(MessageModel).offset(skip).limit(limit)
    messages = session.exec(statement).all()
    return messages