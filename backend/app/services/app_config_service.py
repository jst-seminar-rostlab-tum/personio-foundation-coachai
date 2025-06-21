from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.app_config import AppConfig, ConfigType
from app.schemas.app_config import AppConfigCreate, AppConfigRead


def fetch_all_app_configs(db_session: Session) -> list[AppConfigRead]:
    """
    Retrieve all app configurations.
    """
    statement = select(AppConfig)
    app_configs = db_session.exec(statement).all()
    return [AppConfigRead.from_orm(config) for config in app_configs]


def create_new_app_config(app_config: AppConfigCreate, db_session: Session) -> AppConfigRead:
    """
    Create a new app configuration.
    Automatically assigns the type based on the value.
    """
    existing_config = db_session.get(AppConfig, app_config.key)
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
    db_session.add(db_app_config)
    db_session.commit()
    db_session.refresh(db_app_config)
    return AppConfigRead.from_orm(db_app_config)


def update_existing_app_config(updated_data: AppConfigCreate, db_session: Session) -> AppConfigRead:
    """
    Update an existing app configuration.
    Automatically assigns the type based on the value.
    """
    key = updated_data.key
    app_config = db_session.get(AppConfig, key)
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

    db_session.add(app_config)
    db_session.commit()
    db_session.refresh(app_config)
    return AppConfigRead.from_orm(app_config)


def patch_app_configs(updated_data: list[dict], db_session: Session) -> list[AppConfigRead]:
    """
    Partially update existing app configurations.
    """
    updated_configs = []

    for config_data in updated_data:
        key = config_data.get('key')
        if not key:
            raise HTTPException(status_code=400, detail='Key is required to update AppConfig')

        app_config = db_session.get(AppConfig, key)
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
            if field != 'key' and hasattr(app_config, field):
                setattr(app_config, field, value)

        db_session.add(app_config)
        updated_configs.append(app_config)

    db_session.commit()

    # Refresh all updated configs
    for config in updated_configs:
        db_session.refresh(config)

    return [AppConfigRead.from_orm(config) for config in updated_configs]


def delete_app_config_by_key(key: str, db_session: Session) -> dict:
    """
    Delete an app configuration by its key.
    """
    app_config = db_session.get(AppConfig, key)
    if not app_config:
        raise HTTPException(status_code=404, detail='AppConfig not found')

    db_session.delete(app_config)
    db_session.commit()
    return {'message': 'AppConfig deleted successfully'}
