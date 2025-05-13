from typing import Annotated

from fastapi import APIRouter, Depends

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Annotated[dict, Depends(get_db)]):
    db_message = models.Message(content=message.content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/", response_model=list[schemas.Message])
def read_messages(db: Annotated[dict, Depends(get_db)], skip: int = 0, limit: int = 100):
    messages = db.query(models.Message).offset(skip).limit(limit).all()
    return messages
