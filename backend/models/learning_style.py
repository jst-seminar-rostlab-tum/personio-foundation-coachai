from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.user_profile import UserProfile


class LearningStyle(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(back_populates='preferred_learning_style')


class LearningStyleCreate(SQLModel):
    label: str
    description: str


class LearningStyleRead(SQLModel):
    id: UUID
    label: str
    description: str
