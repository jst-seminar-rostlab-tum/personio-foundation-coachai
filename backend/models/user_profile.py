from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlmodel import Field, Relationship, SQLModel


class UserProfile(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    preferred_language: str = Field(foreign_key="language.code")  # FK to LanguageModel
    role_id: UUID
    experience_id: UUID
    preferred_learning_style: str
    preferred_session_length: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Relationships
    ratings: Optional["Rating"] = Relationship(back_populates="user")
    training_cases: Optional["TrainingCase"] = Relationship(back_populates="user")


# Automatically update `updated_at` before an update
@event.listens_for(UserProfile, "before_update")
def update_timestamp(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()


# Automatically set `deleted_at` and cascade delete related entries
@event.listens_for(UserProfile, "before_delete")
def cascade_delete(mapper, connection, target) -> None:
    target.deleted_at = datetime.utcnow()


# Schema for creating a new UserProfile
class UserProfileCreate(SQLModel):
    preferred_language: str
    role_id: UUID
    experience_id: UUID
    preferred_learning_style: str
    preferred_session_length: str


# Schema for reading UserProfile data
class UserProfileRead(SQLModel):
    id: UUID
    preferred_language: str
    role_id: UUID
    experience_id: UUID
    preferred_learning_style: str
    preferred_session_length: str
    updated_at: datetime
    deleted_at: Optional[datetime]