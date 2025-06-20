from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_admin
from app.schemas.admin_dashboard_stats import AdminDashboardStatsRead
from app.services.admin_dashboard_service import AdminDashboardService

router = APIRouter(prefix='/admin-stats', tags=['Admin Dashboard'])


def get_admin_dashboard_service(
    db: Annotated[DBSession, Depends(get_db_session)],
) -> AdminDashboardService:
    return AdminDashboardService(db)


@router.get(
    '',
    response_model=AdminDashboardStatsRead,
    dependencies=[Depends(require_admin)],
)
def get_admin_dashboard_stats(
    service: Annotated[AdminDashboardService, Depends(get_admin_dashboard_service)],
) -> AdminDashboardStatsRead:
    return service.get_admin_dashboard_stats()
