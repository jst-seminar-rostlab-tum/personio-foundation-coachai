from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class LearningStyle(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(
        back_populates='preferred_learning_style',
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserProfile.preferred_learning_style_id) == LearningStyle.id"
        }
    )


class LearningStyleCreate(SQLModel):
    id: Optional[UUID] = None
    language_code: str
    label: str
    description: str


class LearningStyleRead(SQLModel):
    id: UUID
    language_code: str
    label: str
    description: str
