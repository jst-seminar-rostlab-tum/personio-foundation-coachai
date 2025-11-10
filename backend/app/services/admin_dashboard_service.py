from sqlmodel import Session as DBSession
from sqlmodel import func, select

from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.review import Review
from app.models.user_profile import UserProfile
from app.schemas.admin_dashboard_stats import AdminDashboardStatsRead
from app.services.app_config_service import AppConfigService


class AdminDashboardService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.app_config_service = AppConfigService(db)

    def _get_user_count(self) -> int:
        return self.db.exec(select(func.count()).select_from(UserProfile)).one()

    def _get_review_count(self) -> int:
        return self.db.exec(select(func.count()).select_from(Review)).one()

    def _get_admin_stats(self) -> AdminDashboardStats:
        stats = self.db.exec(select(AdminDashboardStats)).first()
        if not stats:
            stats = AdminDashboardStats()
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(stats)
        return stats

    def get_admin_dashboard_stats(self) -> AdminDashboardStatsRead:
        stats = self._get_admin_stats()

        return AdminDashboardStatsRead(
            total_users=self._get_user_count(),
            total_trainings=stats.total_trainings,
            total_reviews=self._get_review_count(),
            score_sum=stats.score_sum,
            default_daily_session_limit=self.app_config_service.get_default_daily_session_limit(),
        )
