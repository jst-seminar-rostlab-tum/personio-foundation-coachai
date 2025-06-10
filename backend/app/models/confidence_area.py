from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.user_confidence_score import UserConfidenceScore


class ConfidenceArea(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    language_code: str = Field(primary_key=True)
    label: str
    description: str
    min_value: int
    max_value: int
    min_label: str
    max_label: str
    user_confidence_scores: list['UserConfidenceScore'] = Relationship(
        back_populates='confidence_area',
        sa_relationship_kwargs={
            "primaryjoin": "foreign(UserConfidenceScore.area_id) == ConfidenceArea.id"
        }
    )


class ConfidenceAreaCreate(CamelModel):
    id: Optional[UUID] = None
    language_code: str
    label: str
    description: str
    min_value: int
    max_value: int
    min_label: str
    max_label: str


class ConfidenceAreaRead(CamelModel):
    id: UUID
    language_code: str
    label: str
    description: str
    min_value: int
    max_value: int
    min_label: str
    max_label: str
