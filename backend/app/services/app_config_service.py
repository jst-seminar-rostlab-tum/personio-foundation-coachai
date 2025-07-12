from fastapi import HTTPException
from sqlmodel import Session as DBsession
from sqlmodel import select

from app.enums.config_type import ConfigType
from app.models.app_config import AppConfig
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
        return [AppConfigRead(**config.model_dump()) for config in app_configs]

    def create_new_app_config(self, app_config: AppConfigCreate) -> AppConfigRead:
        """
        Create a new app configuration.
        Automatically assigns the type based on the value.
        """
        existing_config = self.db.get(AppConfig, app_config.key)
        if existing_config:
            raise HTTPException(status_code=400, detail='AppConfig with this key already exists')

        self._validate_config_value(app_config.value, app_config.type)

        db_app_config = AppConfig(**app_config.model_dump())
        self.db.add(db_app_config)
        self.db.commit()
        self.db.refresh(db_app_config)
        return AppConfigRead(**db_app_config.model_dump())

    def update_existing_app_config(self, updated_data: AppConfigCreate) -> AppConfigRead:
        """
        Update an existing app configuration.
        Automatically assigns the type based on the value.
        """
        key = updated_data.key
        app_config = self.db.get(AppConfig, key)
        if not app_config:
            raise HTTPException(status_code=404, detail='AppConfig not found')

        for field, value in updated_data.model_dump().items():
            setattr(app_config, field, value)

        self._validate_config_value(app_config.value, app_config.type)

        self.db.add(app_config)
        self.db.commit()
        self.db.refresh(app_config)
        return AppConfigRead(**app_config.model_dump())

    def patch_app_configs(self, updated_data: list[AppConfigCreate]) -> list[AppConfigRead]:
        """
        Partially update existing app configurations.
        """
        updated_configs = []

        for config_data in updated_data:
            key = config_data.key
            if not key:
                raise HTTPException(status_code=400, detail='Key is required to update AppConfig')

            app_config = self.db.get(AppConfig, key)
            if not app_config:
                raise HTTPException(status_code=404, detail=f"AppConfig with key '{key}' not found")

            # Update only the provided fields
            for field, value in config_data.model_dump().items():
                if field != 'key' and hasattr(app_config, field):
                    setattr(app_config, field, value)

            self._validate_config_value(config_data.value, config_data.type)

            self.db.add(app_config)
            updated_configs.append(app_config)

        self.db.commit()

        # Refresh all updated configs
        for config in updated_configs:
            self.db.refresh(config)

        return [AppConfigRead(**config.model_dump()) for config in updated_configs]

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

    def _validate_config_value(self, value: str, config_type: ConfigType) -> None:
        """
        Validate if the value can be typecasted to the specified ConfigType.
        Raises a 422 error if the typecast fails.
        """
        try:
            if config_type == ConfigType.int:
                int(value)  # Try to cast to int
            elif config_type == ConfigType.boolean:
                if value.lower() not in ['true', 'false']:
                    raise ValueError('Invalid boolean value')
            elif config_type == ConfigType.string:
                str(value)  # Strings are always valid
            else:
                raise ValueError('Unsupported ConfigType')
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Value '{value}' cannot be typecasted to {config_type}",
            ) from None
