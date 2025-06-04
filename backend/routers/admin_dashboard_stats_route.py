from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from ..database import get_session
from ..models.admin_dashboard_stats import AdminDashboardStats, AdminDashboardStatsRead
from ..models.user_feedback import UserFeedback
from ..models.user_profile import UserProfile

router = APIRouter(prefix='/admin-stats', tags=['Admin Dashboard'])


@router.get('/', response_model=AdminDashboardStatsRead)
def get_admin_dashboard_stats(
    session: Annotated[Session, Depends(get_session)],
) -> AdminDashboardStatsRead:
    # Get total users
    total_users = session.exec(select(func.count()).select_from(UserProfile)).one()

    # Get total reviews
    total_reviews = session.exec(select(func.count()).select_from(UserFeedback)).one()

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
        daily_token_limit=stats.daily_token_limit,
    )
