from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal["dev", "prod"] = "dev"  # Default to "dev" if not specified

    # Database settings
    DATABASE_URL: str

    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
