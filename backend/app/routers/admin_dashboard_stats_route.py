from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession
from sqlmodel import func, select

from app.database import get_db_session
from app.dependencies import require_admin
from app.models.admin_dashboard_stats import AdminDashboardStats, AdminDashboardStatsRead
from app.models.app_config import AppConfig
from app.models.review import Review
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/admin-stats', tags=['Admin Dashboard'])


@router.get(
    '',
    response_model=AdminDashboardStatsRead,
    dependencies=[Depends(require_admin)],
)
def get_admin_dashboard_stats(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> AdminDashboardStatsRead:
    # Get total users
    total_users = db_session.exec(select(func.count()).select_from(UserProfile)).one()

    # Get total reviews
    total_reviews = db_session.exec(select(func.count()).select_from(Review)).one()

    # Get daily token limit from app_config with key 'dailyUserTokenLimit'
    daily_token_limit = db_session.exec(
        select(AppConfig.value).where(AppConfig.key == 'dailyUserTokenLimit')
    ).first()
    daily_token_limit = int(daily_token_limit) if daily_token_limit is not None else None

    # Get admin stats
    stats = db_session.exec(select(AdminDashboardStats)).first()
    if not stats:
        stats = AdminDashboardStats()
        db_session.add(stats)
        db_session.commit()
        db_session.refresh(stats)

    return AdminDashboardStatsRead(
        total_users=total_users,
        total_trainings=stats.total_trainings,
        total_reviews=total_reviews,
        average_score=stats.average_score,
        daily_token_limit=daily_token_limit,
    )
