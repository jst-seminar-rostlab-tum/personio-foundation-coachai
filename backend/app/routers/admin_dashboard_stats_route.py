from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.database import get_session
from app.models.admin_dashboard_stats import AdminDashboardStats, AdminDashboardStatsRead
from app.models.app_config import AppConfig
from app.models.review import Review
from app.models.user_profile import UserProfile

router = APIRouter(prefix='/admin-stats', tags=['Admin Dashboard'])


@router.get('/', response_model=AdminDashboardStatsRead)
def get_admin_dashboard_stats(
    session: Annotated[Session, Depends(get_session)],
) -> AdminDashboardStatsRead:
    # Get total users
    total_users = session.exec(select(func.count()).select_from(UserProfile)).one()

    # Get total reviews
    total_reviews = session.exec(select(func.count()).select_from(Review)).one()

    # Get daily token limit from app_config with key 'dailyUserTokenLimit'
    daily_token_limit = session.exec(
        select(AppConfig.value).where(AppConfig.key == 'dailyUserTokenLimit')
    ).first()

    # Get admin stats
    stats = session.exec(select(AdminDashboardStats)).first()
    if not stats:
        stats = AdminDashboardStats()
        session.add(stats)
        session.commit()
        session.refresh(stats)

    return AdminDashboardStatsRead(
        total_users=total_users,
        total_trainings=stats.total_trainings,
        total_reviews=total_reviews,
        average_score=stats.average_score,
        daily_token_limit=daily_token_limit,
    )
