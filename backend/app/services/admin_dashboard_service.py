"""Service layer for admin dashboard service."""

from sqlmodel import Session as DBSession
from sqlmodel import func, select

from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.review import Review
from app.models.user_profile import UserProfile
from app.schemas.admin_dashboard_stats import AdminDashboardStatsRead
from app.services.app_config_service import AppConfigService


class AdminDashboardService:
    """Service for assembling admin dashboard statistics."""

    def __init__(self, db: DBSession) -> None:
        """Initialize the service with a database session.

        Parameters:
            db (DBSession): Database session used for queries.
        """
        self.db = db
        self.app_config_service = AppConfigService(db)

    def _get_user_count(self) -> int:
        """Return the total number of user profiles.

        Returns:
            int: Total user count.
        """
        return self.db.exec(select(func.count()).select_from(UserProfile)).one()

    def _get_review_count(self) -> int:
        """Return the total number of reviews.

        Returns:
            int: Total review count.
        """
        return self.db.exec(select(func.count()).select_from(Review)).one()

    def _get_admin_stats(self) -> AdminDashboardStats:
        """Load or initialize admin aggregate statistics.

        Returns:
            AdminDashboardStats: Persisted stats record.
        """
        stats = self.db.exec(select(AdminDashboardStats)).first()
        if not stats:
            stats = AdminDashboardStats()
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(stats)
        return stats

    def get_admin_dashboard_stats(self) -> AdminDashboardStatsRead:
        """Return computed admin dashboard statistics.

        Returns:
            AdminDashboardStatsRead: Aggregated dashboard metrics.
        """
        stats = self._get_admin_stats()

        return AdminDashboardStatsRead(
            total_users=self._get_user_count(),
            total_trainings=stats.total_trainings,
            total_reviews=self._get_review_count(),
            score_sum=stats.score_sum,
            default_daily_session_limit=self.app_config_service.get_default_daily_session_limit(),
        )
