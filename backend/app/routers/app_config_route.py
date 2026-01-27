"""API routes for app config route."""

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
    """Return all app configurations.

    Parameters:
        service (AppConfigService): Service dependency.

    Returns:
        list[AppConfigRead]: Configuration list.
    """
    return service.fetch_all_app_configs()


@router.post('', response_model=AppConfigRead, dependencies=[Depends(require_admin)])
def create_app_config(
    app_config: AppConfigCreate,
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> AppConfigRead:
    """Create a new app configuration.

    Parameters:
        app_config (AppConfigCreate): Configuration payload.
        service (AppConfigService): Service dependency.

    Returns:
        AppConfigRead: Created configuration.
    """
    return service.create_new_app_config(app_config)


@router.put('', response_model=AppConfigRead, dependencies=[Depends(require_admin)])
def update_app_config(
    updated_data: AppConfigCreate,
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> AppConfigRead:
    """Update an existing app configuration.

    Parameters:
        updated_data (AppConfigCreate): Configuration payload.
        service (AppConfigService): Service dependency.

    Returns:
        AppConfigRead: Updated configuration.
    """
    return service.update_existing_app_config(updated_data)


@router.patch('', response_model=list[AppConfigRead], dependencies=[Depends(require_admin)])
def patch_app_config(
    updated_data: list[AppConfigCreate],
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> list[AppConfigRead]:
    """Partially update existing app configurations.

    Parameters:
        updated_data (list[AppConfigCreate]): Configuration payload list.
        service (AppConfigService): Service dependency.

    Returns:
        list[AppConfigRead]: Updated configurations.
    """
    return service.patch_app_configs(updated_data)


@router.delete('/{key}', response_model=dict, dependencies=[Depends(require_admin)])
def delete_app_config(
    key: str,
    service: Annotated[AppConfigService, Depends(get_app_config_service)],
) -> dict:
    """Delete an app configuration by key.

    Parameters:
        key (str): Configuration key.
        service (AppConfigService): Service dependency.

    Returns:
        dict: Deletion confirmation.
    """
    return service.delete_app_config_by_key(key)
