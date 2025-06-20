from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_category import ConversationCategory
from app.schemas.conversation_category import ConversationCategoryRead

router = APIRouter(prefix='/conversation-categories', tags=['Conversation Categories'])


@router.get('', response_model=list[ConversationCategoryRead], dependencies=[Depends(require_user)])
def get_conversation_categories(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[ConversationCategory]:
    """
    Retrieve all conversation categories.
    """
    statement = select(ConversationCategory)
    categories = db_session.exec(statement).all()
    return list(categories)
