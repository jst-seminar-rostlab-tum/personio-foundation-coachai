from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.conversation_category import (
    ConversationCategory,
    ConversationCategoryCreate,
    ConversationCategoryRead,
)

router = APIRouter(prefix='/conversation-categories', tags=['Conversation Categories'])


@router.get('/', response_model=list[ConversationCategoryRead])
def get_conversation_categories(
    session: Annotated[Session, Depends(get_session)],
) -> list[ConversationCategory]:
    """
    Retrieve all conversation categories.
    """
    statement = select(ConversationCategory)
    categories = session.exec(statement).all()
    return list(categories)


@router.post('/', response_model=ConversationCategoryRead)
def create_conversation_category(
    category: ConversationCategoryCreate, session: Annotated[Session, Depends(get_session)]
) -> ConversationCategory:
    """
    Create a new conversation category.
    """
    db_category = ConversationCategory(**category.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.put('/{category_id}', response_model=ConversationCategoryRead)
def update_conversation_category(
    category_id: UUID,
    updated_data: dict,
    session: Annotated[Session, Depends(get_session)],
) -> ConversationCategory:
    """
    Update an existing conversation category.
    """
    category = session.get(ConversationCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    for key, value in updated_data.items():
        if hasattr(category, key):  # Ensure the field exists in the model
            setattr(
                category,
                key,
                value if value is not None else getattr(ConversationCategory, key).default,
            )

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete('/{category_id}', response_model=dict)
def delete_conversation_category(
    category_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a conversation category.
    """
    category = session.get(ConversationCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail='Category not found')

    session.delete(category)
    session.commit()
    return {'message': 'Category deleted successfully'}
