from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session as DBSession

from app.database import get_db_session
from app.dependencies import require_admin, require_user
from app.schemas.app_config import AppConfigCreate, AppConfigRead
from app.services.app_config_service import (
    create_new_app_config,
    delete_app_config_by_key,
    fetch_all_app_configs,
    patch_app_configs,
    update_existing_app_config,
)

router = APIRouter(prefix='/app-config', tags=['App Config'])


@router.get('', response_model=list[AppConfigRead], dependencies=[Depends(require_user)])
def get_app_configs(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[AppConfigRead]:
    """
    Retrieve all app configurations.
    """
    return fetch_all_app_configs(db_session)


@router.post('', response_model=AppConfigRead, dependencies=[Depends(require_admin)])
def create_app_config(
    app_config: AppConfigCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> AppConfigRead:
    """
    Create a new app configuration.
    """
    return create_new_app_config(app_config, db_session)


@router.put('', response_model=AppConfigRead, dependencies=[Depends(require_admin)])
def update_app_config(
    updated_data: AppConfigCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> AppConfigRead:
    """
    Update an existing app configuration.
    """
    return update_existing_app_config(updated_data, db_session)


@router.patch('', response_model=list[AppConfigRead], dependencies=[Depends(require_admin)])
def patch_app_config(
    updated_data: list[dict],
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[AppConfigRead]:
    """
    Partially update existing app configurations.
    """
    return patch_app_configs(updated_data, db_session)


@router.delete('/{key}', response_model=dict, dependencies=[Depends(require_admin)])
def delete_app_config(key: str, db_session: Annotated[DBSession, Depends(get_db_session)]) -> dict:
    """
    Delete an app configuration.
    """
    return delete_app_config_by_key(key, db_session)
