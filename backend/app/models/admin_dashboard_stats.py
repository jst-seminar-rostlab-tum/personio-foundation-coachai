from uuid import UUID, uuid4

from sqlmodel import Field

from app.models.camel_case import CamelModel


class AdminDashboardStats(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    total_trainings: int = Field(default=0)
    average_score: int = Field(default=82)  # mock value
