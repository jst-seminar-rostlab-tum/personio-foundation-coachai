from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class Experience(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    # Relationships
    user: list['UserProfile'] = Relationship(back_populates='experience')


# Schema for creating a new Experience
class ExperienceCreate(SQLModel):
    label: str
    description: str


# Schema for reading Experience data
class ExperienceRead(SQLModel):
    id: UUID
    label: str
    description: str
