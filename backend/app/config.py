from typing import Literal
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.data.dummy_data import MockUserIdsEnum


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'

    SUPABASE_PASSWORD: str = ''
    SUPABASE_DB: str = 'postgres'
    SUPABASE_PORT: int = 5432
    SUPABASE_KONG_HTTP_PORT: int = 8001
    SUPABASE_HOST: str = 'localhost'

    SUPABASE_URL: str = ''
    SUPABASE_DB_URL: str = ''

    SUPABASE_ANON_KEY: str = ''
    SUPABASE_SERVICE_ROLE_KEY: str = ''
    SUPABASE_JWT_SECRET: str = ''

    GEMINI_API_KEY: str = ''
    OPENAI_API_KEY: str = ''

    # Twilio settings
    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_PHONE_NUMBER: str = ''

    ENABLE_AI: bool = False
    FORCE_CHEAP_MODEL: bool = True

    DEV_MODE_SKIP_AUTH: bool = False
    DEV_MODE_MOCK_USER_ID: UUID = MockUserIdsEnum.USER.value

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
