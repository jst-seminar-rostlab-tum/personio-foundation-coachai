from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_profile import UserProfile


class SessionLength(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)
    label: str
    description: str

    user_profiles: list['UserProfile'] = Relationship(
        back_populates='preferred_session_length',
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserProfile.preferred_session_length_id) == SessionLength.id"
        })


class SessionLengthCreate(CamelModel):
    id: Optional[UUID] = None
    language_code: str
    label: str
    description: str


class SessionLengthRead(CamelModel):
    language_code: str
    id: UUID
    label: str
    description: str
