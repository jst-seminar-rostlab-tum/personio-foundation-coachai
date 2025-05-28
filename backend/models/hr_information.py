from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector  # Corrected import for pgvector
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel


class HrInformation(SQLModel, table=True):
    __tablename__ = 'hr_information'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    meta_data: Optional[dict] = Field(sa_column=Column(JSONB))
    embedding: list[float] = Field(
        sa_column=Column(Vector(768))
    )  # Assuming 768-dimensional vectors
