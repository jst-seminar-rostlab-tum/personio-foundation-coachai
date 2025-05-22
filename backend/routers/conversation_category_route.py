from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.conversation_category_model import (
    ConversationCategoryCreate,
    ConversationCategoryModel,
    ConversationCategoryRead,
)

router = APIRouter(prefix="/conversation-categories", tags=["Conversation Categories"])


@router.get("/", response_model=List[ConversationCategoryRead])
def get_conversation_categories(
    session: Annotated[Session, Depends(get_session)]
) -> List[ConversationCategoryRead]:
    """
    Retrieve all conversation categories.
    """
    statement = select(ConversationCategoryModel)
    categories = session.exec(statement).all()
    return categories


@router.post("/", response_model=ConversationCategoryRead)
def create_conversation_category(
    category: ConversationCategoryCreate, session: Annotated[Session, Depends(get_session)]
) -> ConversationCategoryModel:
    """
    Create a new conversation category.
    """
    db_category = ConversationCategoryModel(**category.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=ConversationCategoryRead)
def update_conversation_category(
    category_id: UUID,
    updated_data: ConversationCategoryCreate,
    session: Annotated[Session, Depends(get_session)],
) -> ConversationCategoryModel:
    """
    Update an existing conversation category.
    """
    category = session.get(ConversationCategoryModel, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in updated_data.dict().items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", response_model=dict)
def delete_conversation_category(
    category_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a conversation category.
    """
    category = session.get(ConversationCategoryModel, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"message": "Category deleted successfully"}