from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column as SAColumn
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    pass


class HrInformation(CamelModel, table=True):
    __tablename__ = 'hr_information'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    meta_data: Optional[dict] = Field(default=None, sa_column=SAColumn('metadata', JSONB))
    embedding: list[float] = Field(sa_column=SAColumn(Vector(768)))
