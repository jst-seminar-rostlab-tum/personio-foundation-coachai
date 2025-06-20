from app.models.camel_case import CamelModel


# Schema for reading admin dashboard stats
class AdminDashboardStatsRead(CamelModel):
    total_users: int  # number of users in the system
    total_trainings: int
    total_reviews: int  # number of reviews
    average_score: int
    daily_token_limit: int | None  # daily token limit retrieved from app_config table
