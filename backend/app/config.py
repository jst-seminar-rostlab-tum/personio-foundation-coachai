from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.interfaces import MockUser, MockUserIdsEnum


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
    TWILIO_VERIFY_SERVICE_SID: str = ''

    ENABLE_AI: bool = False
    FORCE_CHEAP_MODEL: bool = True

    DEV_MODE_SKIP_AUTH: bool = False
    DEV_MODE_MOCK_USER_ID: UUID = MockUserIdsEnum.USER.value

    DEMO_USER_EMAIL: str = 'mockuser@example.com'
    DEMO_USER_PASSWORD: str = 'mockuserpassword'

    DEMO_ADMIN_EMAIL: str = 'mockadmin@example.com'
    DEMO_ADMIN_PASSWORD: str = 'mockadminpassword'

    # GCP settings
    GCP_PROJECT_ID: str
    GCP_PRIVATE_KEY_ID: str
    GCP_PRIVATE_KEY: str
    GCP_CLIENT_EMAIL: str
    GCP_CLIENT_ID: str
    GCP_AUTH_URI: str
    GCP_TOKEN_URI: str
    GCP_AUTH_PROVIDER_CERT_URL: str
    GCP_CLIENT_CERT_URL: str
    GCP_UNIVERSE_DOMAIN: str = 'googleapis.com'

    @property
    def mock_user_data(self) -> MockUser:
        return MockUser(
            email=self.DEMO_USER_EMAIL,
            password=self.DEMO_USER_PASSWORD,
            phone='+1234567890',
            full_name='Demo User',
        )

    @property
    def mock_admin_data(self) -> MockUser:
        return MockUser(
            email=self.DEMO_ADMIN_EMAIL,
            password=self.DEMO_ADMIN_PASSWORD,
            phone='+1987654321',
            full_name='Admin',
        )

    model_config = SettingsConfigDict(env_file=Path(__file__).parent / '.env', extra='ignore')


settings = Settings()
