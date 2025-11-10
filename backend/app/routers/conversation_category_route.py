from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.dependencies.auth import require_user
from app.dependencies.database import get_db_session
from app.schemas.conversation_category import ConversationCategoryRead
from app.services.conversation_category_service import ConversationCategoryService

router = APIRouter(prefix='/conversation-categories', tags=['Conversation Categories'])


def get_conversation_category_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ConversationCategoryService:
    """
    Dependency factory to inject the ConversationCategoryService.
    """
    return ConversationCategoryService(db_session)


@router.get('', response_model=list[ConversationCategoryRead], dependencies=[Depends(require_user)])
def get_conversation_categories(
    service: Annotated[ConversationCategoryService, Depends(get_conversation_category_service)],
) -> list[ConversationCategoryRead]:
    """
    Retrieve all conversation categories.
    """
    return service.fetch_all_conversation_categories()
