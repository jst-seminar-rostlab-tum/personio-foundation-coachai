from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class LearningStyle(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(back_populates='preferred_learning_style')


class LearningStyleCreate(CamelModel):
    label: str
    description: str


class LearningStyleRead(CamelModel):
    id: UUID
    label: str
    description: str
