from pydantic import Field

from app.models.camel_case import CamelModel


# Schema for reading admin dashboard stats
class AdminDashboardStatsRead(CamelModel):
    total_users: int = Field(..., description='Number of users in the system')
    total_trainings: int = Field(..., description='Total number of trainig sessions')
    total_reviews: int = Field(..., description='Number of reviews')
    score_sum: float = Field(..., description='Sum of all scores')
    default_daily_session_limit: int
