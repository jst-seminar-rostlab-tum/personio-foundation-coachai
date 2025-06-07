from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'
    postgres_host: str = 'localhost'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'app_db'
    postgres_port: str = '5432'
    database_url: str | None = None

    SUPABASE_URL: str = ''
    SUPABASE_KEY: str = ''
    SUPABASE_JWT_SECRET: str = ''

    GEMINI_API_KEY: str = ''

    ssl_cert_url: str = 'https://test.com'
    ssl_cert_dir: str = 'cert/'  # Must be either /tmp or relative
    ssl_cert_name: str = 'prod-ca-2021.pem'

    # Twilio settings
    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_PHONE_NUMBER: str = ''

    ENABLE_AI: bool = False
    FORCE_CHEAP_MODEL: bool = True

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
