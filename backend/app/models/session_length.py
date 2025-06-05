from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class SessionLength(BaseModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(back_populates='preferred_session_length')


class SessionLengthCreate(BaseModel):
    label: str
    description: str


class SessionLengthRead(BaseModel):
    id: UUID
    label: str
    description: str
