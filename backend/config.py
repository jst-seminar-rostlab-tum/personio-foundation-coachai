from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'
    postgres_host: str = 'localhost'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres_prod'
    postgres_db: str = 'app_db'
    postgres_port: str = '5432'
    # Twilio settings
    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_PHONE_NUMBER: str = ''

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
