from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class Role(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    # Relationships
    user_profiles: list['UserProfile'] = Relationship(back_populates='role')  # Use string reference


# Schema for creating a new Role
class RoleCreate(SQLModel):
    label: str
    description: str


# Schema for reading Role data
class RoleRead(SQLModel):
    id: UUID
    label: str
    description: str
