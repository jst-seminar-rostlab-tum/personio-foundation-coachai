from sqlmodel import Session as DBSession
from sqlmodel import func, select

from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.app_config import AppConfig
from app.models.review import Review
from app.models.user_profile import UserProfile
from app.schemas.admin_dashboard_stats import AdminDashboardStatsRead


class AdminDashboardService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def _get_user_count(self) -> int:
        return self.db.exec(select(func.count()).select_from(UserProfile)).one()

    def _get_review_count(self) -> int:
        return self.db.exec(select(func.count()).select_from(Review)).one()

    def _get_daily_token_limit(self) -> int | None:
        daily_token_limit = self.db.exec(
            select(AppConfig.value).where(AppConfig.key == 'dailyUserTokenLimit')
        ).first()
        return int(daily_token_limit) if daily_token_limit is not None else None

    def _get_admin_stats(self) -> AdminDashboardStats:
        stats = self.db.exec(select(AdminDashboardStats)).first()
        if not stats:
            stats = AdminDashboardStats()
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(stats)
        return stats

    def get_admin_dashboard_stats(self) -> AdminDashboardStatsRead:
        # Get total users
        total_users = self._get_user_count()

        # Get total reviews
        total_reviews = self._get_review_count()

        # Get daily token limit from app_config with key 'dailyUserTokenLimit'
        daily_token_limit = self._get_daily_token_limit()

        # Get admin stats
        stats = self._get_admin_stats()

        return AdminDashboardStatsRead(
            total_users=total_users,
            total_trainings=stats.total_trainings,
            total_reviews=total_reviews,
            average_score=stats.average_score,
            daily_token_limit=daily_token_limit,
        )
