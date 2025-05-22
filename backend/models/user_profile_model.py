from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.rating_model import RatingModel
    from backend.models.training_case_model import TrainingCaseModel


class UserProfileModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    preferred_language: str = Field(foreign_key='languagemodel.code')  # FK to LanguageModel
    role_id: UUID
    experience_id: UUID
    preferred_learning_style: str
    preferred_session_length: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Relationships
    ratings: Optional['RatingModel'] = Relationship(back_populates='user')
    training_cases: Optional['TrainingCaseModel'] = Relationship(back_populates='user')


# Automatically update `updated_at` before an update
@event.listens_for(UserProfileModel, 'before_update')
def update_timestamp(mapper: Mapper, connection: Connection, target: 'UserProfileModel') -> None:
    target.updated_at = datetime.utcnow()


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
