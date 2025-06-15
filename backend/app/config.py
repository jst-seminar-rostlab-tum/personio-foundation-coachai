from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.data.mock_user_ids_enum import MockUserIdsEnum


class MockUser(BaseModel):
    email: str
    password: str
    phone: str
    full_name: str


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'
    postgres_host: str = 'localhost'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'app_db'
    postgres_port: str = '5432'
    database_url: str | None = None

    SUPABASE_URL: str = ''
    SUPABASE_ANON_KEY: str = ''
    SUPABASE_SERVICE_ROLE_KEY: str = ''
    SUPABASE_JWT_SECRET: str = ''

    GEMINI_API_KEY: str = ''
    OPENAI_API_KEY: str = ''

    CORS_ORIGIN: str = 'http://localhost:3000'

    ssl_cert_url: str = 'https://test.com'
    ssl_cert_dir: str = 'cert/'  # Must be either /tmp or relative
    ssl_cert_name: str = 'prod-ca-2021.pem'

    # Twilio settings
    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_PHONE_NUMBER: str = ''

    ENABLE_AI: bool = False
    FORCE_CHEAP_MODEL: bool = True

    DEV_MODE_SKIP_AUTH: bool = False
    DEV_MODE_MOCK_USER_ID: UUID = MockUserIdsEnum.USER.value

    MOCK_USER_DATA: MockUser = MockUser(
        email='mockuser@example.com',
        password='mockuserpassword',
        phone='+1234567890',
        full_name='Mock User',
    )
    MOCK_ADMIN_DATA: MockUser = MockUser(
        email='mockadmin@example.com',
        password='mockadminpassword',
        phone='+1987654321',
        full_name='Mock Admin',
    )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
