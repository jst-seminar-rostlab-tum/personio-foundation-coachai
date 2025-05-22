from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel


class ConversationCategoryModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
    icon_uri: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    training_cases: List["TrainingCaseModel"] = Relationship(back_populates="category")
    
@event.listens_for(ConversationCategoryModel, "before_update")
def update_timestamp(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()
# Schema for creating a new ConversationCategory
class ConversationCategoryCreate(SQLModel):
    name: str
    icon_uri: str
    description: str

# Schema for reading ConversationCategory data
class ConversationCategoryRead(SQLModel):
    id: UUID
    name: str
    icon_uri: str
    description: str
    created_at: datetime
    updated_at: datetime