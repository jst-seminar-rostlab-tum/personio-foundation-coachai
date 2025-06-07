from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class Role(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserProfile.role_id) == Role.id"
        }
    )

# Schema for creating a new Role
class RoleCreate(SQLModel):
    # `id` is optional for creation, it will be generated automatically,
    # if we want to add a new language to existing id then need to specify it
    id: Optional[UUID] = None
    language_code: str
    label: str
    description: str


# Schema for reading Role data
class RoleRead(SQLModel):
    id: UUID
    language_code: str
    label: str
    description: str
