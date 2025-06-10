from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column  # Import Column directly
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class HrInformation(SQLModel, table=True):
    __tablename__ = 'hr_information'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    meta_data: dict | None = Field(default=None, sa_column=Column('metadata', JSONB))
    embedding: list[float] = Field(sa_column=Column(Vector(768)))
