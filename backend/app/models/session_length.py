from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class SessionLength(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(back_populates='preferred_session_length')


class SessionLengthCreate(SQLModel):
    label: str
    description: str


class SessionLengthRead(SQLModel):
    id: UUID
    label: str
    description: str
