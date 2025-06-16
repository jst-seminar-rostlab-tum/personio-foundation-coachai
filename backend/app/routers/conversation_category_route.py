from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.dependencies import require_user
from app.models.conversation_category import (
    ConversationCategory,
    ConversationCategoryCreate,
    ConversationCategoryRead,
)

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


@router.post('', response_model=ConversationCategoryRead)
def create_conversation_category(
    category: ConversationCategoryCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> ConversationCategory:
    """
    Create a new conversation category.
    """
    db_category = ConversationCategory(**category.dict())
    db_session.add(db_category)
    db_session.commit()
    db_session.refresh(db_category)
    return db_category


@router.put('/{category_id}', response_model=ConversationCategoryRead)
def update_conversation_category(
    category_id: str,
    updated_data: dict,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ConversationCategory:
    """
    Update an existing conversation category.
    """
    category = db_session.get(ConversationCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    for key, value in updated_data.items():
        if hasattr(category, key):  # Ensure the field exists in the model
            setattr(
                category,
                key,
                value if value is not None else getattr(ConversationCategory, key).default,
            )

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@router.delete('/{category_id}', response_model=dict)
def delete_conversation_category(
    category_id: str, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a conversation category.
    """
    category = db_session.get(ConversationCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    db_session.delete(category)
    db_session.commit()
    return {'message': 'Category deleted successfully'}
