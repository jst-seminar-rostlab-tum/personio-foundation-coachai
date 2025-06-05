from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class Experience(BaseModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    # Relationships
    user_profiles: list['UserProfile'] = Relationship(back_populates='experiences')


# Schema for creating a new Experience
class ExperienceCreate(BaseModel):
    label: str
    description: str


# Schema for reading Experience data
class ExperienceRead(BaseModel):
    id: UUID
    label: str
    description: str
