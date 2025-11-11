from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import require_admin, require_user
from app.schemas.app_config import AppConfigCreate, AppConfigRead
from app.services.app_config_service import AppConfigService, get_app_config_service

router = APIRouter(prefix='/app-configs', tags=['App Config'])


@router.get('', response_model=list[AppConfigRead], dependencies=[Depends(require_user)])
def get_app_configs(
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> list[AppConfigRead]:
    """
    Retrieve all app configurations.
    """
    return service.fetch_all_app_configs()


@router.post('', response_model=AppConfigRead, dependencies=[Depends(require_admin)])
def create_app_config(
    app_config: AppConfigCreate,
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> AppConfigRead:
    """
    Create a new app configuration.
    """
    return service.create_new_app_config(app_config)


@router.put('', response_model=AppConfigRead, dependencies=[Depends(require_admin)])
def update_app_config(
    updated_data: AppConfigCreate,
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> AppConfigRead:
    """
    Update an existing app configuration.
    """
    return service.update_existing_app_config(updated_data)


@router.patch('', response_model=list[AppConfigRead], dependencies=[Depends(require_admin)])
def patch_app_config(
    updated_data: list[AppConfigCreate],
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> list[AppConfigRead]:
    """
    Partially update existing app configurations.
    """
    return service.patch_app_configs(updated_data)


@router.delete('/{key}', response_model=dict, dependencies=[Depends(require_admin)])
def delete_app_config(
    key: str,
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> dict:
    """
    Delete an app configuration.
    """
    return service.delete_app_config_by_key(key)
