from typing import Annotated

from fastapi import Depends
from sqlmodel import Session as DBSession

from app.dependencies.database import get_db_session
from app.services.app_config_service import AppConfigService


def get_app_config_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> AppConfigService:
    """
    Dependency factory to inject the AppConfigService.
    """
    return AppConfigService(db_session)
