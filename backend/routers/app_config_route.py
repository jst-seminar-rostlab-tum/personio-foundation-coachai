from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.app_config import AppConfig, AppConfigCreate, AppConfigRead, ConfigType

router = APIRouter(prefix='/app-config', tags=['App Config'])


@router.get('/', response_model=list[AppConfigRead])
def get_app_configs(
    session: Annotated[Session, Depends(get_session)],
) -> list[AppConfig]:
    """
    Retrieve all app configurations.
    """
    statement = select(AppConfig)
    app_configs = session.exec(statement).all()
    return list(app_configs)


@router.post('/', response_model=AppConfigRead)
def create_app_config(
    app_config: AppConfigCreate, session: Annotated[Session, Depends(get_session)]
) -> AppConfig:
    """
    Create a new app configuration.
    Automatically assigns the type based on the value.
    """
    # Check if the key already exists
    existing_config = session.get(AppConfig, app_config.key)
    if existing_config:
        raise HTTPException(status_code=400, detail='AppConfig with this key already exists')

    # Automatically determine the type based on the value
    if app_config.value.lower() in ['true', 'false']:
        app_config.type = ConfigType.boolean
    elif app_config.value.isdigit():
        app_config.type = ConfigType.int
    else:
        app_config.type = ConfigType.string

    db_app_config = AppConfig(**app_config.dict())
    session.add(db_app_config)
    session.commit()
    session.refresh(db_app_config)
    return db_app_config


@router.put('/', response_model=AppConfigRead)
def update_app_config(
    updated_data: AppConfigCreate,
    session: Annotated[Session, Depends(get_session)],
) -> AppConfig:
    """
    Update an existing app configuration.
    Automatically assigns the type based on the value.
    """
    key = updated_data.key
    app_config = session.get(AppConfig, key)
    if not app_config:
        raise HTTPException(status_code=404, detail='AppConfig not found')

    # Automatically determine the type based on the value
    if updated_data.value.lower() in ['true', 'false']:
        updated_data.type = ConfigType.boolean
    elif updated_data.value.isdigit():
        updated_data.type = ConfigType.int
    else:
        updated_data.type = ConfigType.string

    for field, value in updated_data.dict().items():
        setattr(app_config, field, value)

    session.add(app_config)
    session.commit()
    session.refresh(app_config)
    return app_config


@router.patch('/', response_model=list[AppConfigRead])
def patch_app_config(
    updated_data: list[dict],  # Expect partial data for PATCH
    session: Annotated[Session, Depends(get_session)],
) -> list[AppConfig]:
    """
    Partially update an existing app configuration.
    Automatically assigns the type based on the value.
    """
    updated_configs = []

    for config_data in updated_data:
        key = config_data.get('key')
        if not key:
            raise HTTPException(status_code=400, detail='Key is required to update AppConfig')

        app_config = session.get(AppConfig, key)
        if not app_config:
            raise HTTPException(status_code=404, detail=f"AppConfig with key '{key}' not found")

        # Automatically determine the type based on the value
        value = config_data.get('value')
        if value:
            if value.lower() in ['true', 'false']:
                config_data['type'] = ConfigType.boolean
            elif value.isdigit():
                config_data['type'] = ConfigType.int
            else:
                config_data['type'] = ConfigType.string

        # Update only the provided fields
        for field, value in config_data.items():
            if field != 'key' and hasattr(
                app_config, field
            ):  # Ensure the field exists in the model
                setattr(app_config, field, value)

        session.add(app_config)
        updated_configs.append(app_config)

    session.commit()

    # Refresh all updated configs
    for config in updated_configs:
        session.refresh(config)

    return list(updated_configs)


@router.delete('/{key}', response_model=dict)
def delete_app_config(key: str, session: Annotated[Session, Depends(get_session)]) -> dict:
    """
    Delete an app configuration.
    """
    app_config = session.get(AppConfig, key)
    if not app_config:
        raise HTTPException(status_code=404, detail='AppConfig not found')

    session.delete(app_config)
    session.commit()
    return {'message': 'AppConfig deleted successfully'}
