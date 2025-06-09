from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class Experience(CamelModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(
        back_populates='experience',
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserProfile.experience_id) == Experience.id"
        }
    )


# Schema for creating a new Experience
class ExperienceCreate(CamelModel):
    id: Optional[UUID] = None
    language_code: str
    label: str
    description: str


# Schema for reading Experience data
class ExperienceRead(CamelModel):
    id: UUID
    language_code: str
    label: str
    description: str
