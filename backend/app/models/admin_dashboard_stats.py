from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AdminDashboardStats(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    total_trainings: int = Field(default=0)
    average_score: int = Field(default=82)  # mock value


# Schema for reading admin dashboard stats
class AdminDashboardStatsRead(SQLModel):
    total_users: int  # number of users in the system
    total_trainings: int
    total_reviews: int  # number of reviews
    average_score: int
    daily_token_limit: int | None  # daily token limit retrieved from app_config table
