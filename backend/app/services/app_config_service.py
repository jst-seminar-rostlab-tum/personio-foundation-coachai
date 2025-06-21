from fastapi import HTTPException
from sqlmodel import Session as DBsession
from sqlmodel import select

from app.models.app_config import AppConfig, ConfigType
from app.schemas.app_config import AppConfigCreate, AppConfigRead


class AppConfigService:
    def __init__(self, db: DBsession) -> None:
        self.db = db

    def fetch_all_app_configs(self) -> list[AppConfigRead]:
        """
        Retrieve all app configurations.
        """
        statement = select(AppConfig)
        app_configs = self.db.exec(statement).all()
        return [AppConfigRead.from_orm(config) for config in app_configs]

    def create_new_app_config(self, app_config: AppConfigCreate) -> AppConfigRead:
        """
        Create a new app configuration.
        Automatically assigns the type based on the value.
        """
        existing_config = self.db.get(AppConfig, app_config.key)
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
        self.db.add(db_app_config)
        self.db.commit()
        self.db.refresh(db_app_config)
        return AppConfigRead.from_orm(db_app_config)

    def update_existing_app_config(self, updated_data: AppConfigCreate) -> AppConfigRead:
        """
        Update an existing app configuration.
        Automatically assigns the type based on the value.
        """
        key = updated_data.key
        app_config = self.db.get(AppConfig, key)
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

        self.db.add(app_config)
        self.db.commit()
        self.db.refresh(app_config)
        return AppConfigRead.from_orm(app_config)

    def patch_app_configs(self, updated_data: list[dict]) -> list[AppConfigRead]:
        """
        Partially update existing app configurations.
        """
        updated_configs = []

        for config_data in updated_data:
            key = config_data.get('key')
            if not key:
                raise HTTPException(status_code=400, detail='Key is required to update AppConfig')

            app_config = self.db.get(AppConfig, key)
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

            self.db.add(app_config)
            updated_configs.append(app_config)

        self.db.commit()

        # Refresh all updated configs
        for config in updated_configs:
            self.db.refresh(config)

        return [AppConfigRead.from_orm(config) for config in updated_configs]

    def delete_app_config_by_key(self, key: str) -> dict:
        """
        Delete an app configuration by its key.
        """
        app_config = self.db.get(AppConfig, key)
        if not app_config:
            raise HTTPException(status_code=404, detail='AppConfig not found')

        self.db.delete(app_config)
        self.db.commit()
        return {'message': 'AppConfig deleted successfully'}
