from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column as SAColumn
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class HrInformation(SQLModel, table=True):
    __tablename__ = 'hr_information'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    meta_data: Optional[dict] = Field(default=None, sa_column=SAColumn('metadata', JSONB))
    embedding: list[float] = Field(sa_column=SAColumn(Vector(768)))
