"""Service layer for app config service."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session as DBSession
from sqlmodel import Session as DBsession
from sqlmodel import select

from app.dependencies.database import get_db_session
from app.enums.config_type import ConfigType
from app.models.app_config import AppConfig
from app.schemas.app_config import AppConfigCreate, AppConfigRead


class AppConfigService:
    """Service for managing application configuration records."""

    def __init__(self, db: DBsession) -> None:
        """Initialize the service with a database session.

        Parameters:
            db (DBsession): Database session used for persistence.
        """
        self.db = db

    def fetch_all_app_configs(self) -> list[AppConfigRead]:
        """Retrieve all application configurations.

        Returns:
            list[AppConfigRead]: All configuration records.
        """
        statement = select(AppConfig)
        app_configs = self.db.exec(statement).all()
        return [AppConfigRead(**config.model_dump()) for config in app_configs]

    def create_new_app_config(self, app_config: AppConfigCreate) -> AppConfigRead:
        """Create a new application configuration entry.

        Parameters:
            app_config (AppConfigCreate): Configuration payload.

        Returns:
            AppConfigRead: Created configuration.

        Raises:
            HTTPException: If the key already exists or validation fails.
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
        """Update an existing application configuration entry.
        Automatically assigns the type based on the value.

        Parameters:
            updated_data (AppConfigCreate): Updated configuration payload.

        Returns:
            AppConfigRead: Updated configuration.

        Raises:
            HTTPException: If the configuration does not exist or validation fails.
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
        """Partially update existing app configurations.

        Parameters:
            updated_data (list[AppConfigCreate]): List of updates.

        Returns:
            list[AppConfigRead]: Updated configurations.

        Raises:
            HTTPException: If keys are missing or records are not found.
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
        """Delete an application configuration by key.

        Parameters:
            key (str): Configuration key to delete.

        Returns:
            dict: Deletion confirmation message.

        Raises:
            HTTPException: If the configuration is not found.
        """
        app_config = self.db.get(AppConfig, key)
        if not app_config:
            raise HTTPException(status_code=404, detail='AppConfig not found')

        self.db.delete(app_config)
        self.db.commit()
        return {'message': 'AppConfig deleted successfully'}

    def _validate_config_value(self, value: str, config_type: ConfigType) -> None:
        """Validate if the value can be typecasted to the specified ConfigType.

        Parameters:
            value (str): Raw configuration value.
            config_type (ConfigType): Declared configuration type.

        Raises:
            HTTPException: If the value cannot be cast to the configured type.
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

    def get_value(self, key: str) -> str | None:
        """Fetch a configuration value by key.

        Parameters:
            key (str): Configuration key.

        Returns:
            str | None: Stored configuration value, if present.
        """
        statement = select(AppConfig.value).where(AppConfig.key == key)
        return self.db.scalar(statement)

    def get_default_daily_session_limit(self) -> int:
        """Return the default daily session limit for users.

        Returns:
            int: Daily session limit, or 0 when unset.

        Raises:
            HTTPException: If the stored value cannot be cast to int.
        """
        value = self.get_value('defaultDailyUserSessionLimit')

        if value is None:
            return 0

        try:
            return int(value)
        except (TypeError, ValueError) as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            ) from err


def get_app_config_service(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> AppConfigService:
    """Provide an AppConfigService instance for dependency injection.

    Parameters:
        db_session (DBSession): Database session dependency.

    Returns:
        AppConfigService: Configured service instance.
    """
    return AppConfigService(db_session)
