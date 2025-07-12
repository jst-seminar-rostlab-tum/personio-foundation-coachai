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

    def _get_daily_session_limit(self) -> int:
        daily_session_limit = self.db.exec(
            select(AppConfig.value).where(AppConfig.key == 'dailyUserSessionLimit')
        ).first()
        return int(daily_session_limit) if daily_session_limit is not None else 0

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

        # Get daily session limit from app_config with key 'dailyUserSessionLimit'
        daily_session_limit = self._get_daily_session_limit()

        # Get admin stats
        stats = self._get_admin_stats()

        return AdminDashboardStatsRead(
            total_users=total_users,
            total_trainings=stats.total_trainings,
            total_reviews=total_reviews,
            score_sum=stats.score_sum,
            daily_session_limit=daily_session_limit,
        )
