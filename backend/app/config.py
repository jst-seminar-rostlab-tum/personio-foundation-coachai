"""Application configuration and settings."""

from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.interfaces import MockUser, MockUserIdsEnum


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Parameters:
        stage (Literal['dev', 'prod']): Deployment stage identifier.
        postgres_host (str): Postgres hostname.
        postgres_user (str): Postgres username.
        postgres_password (str): Postgres password.
        postgres_db (str): Postgres database name.
        postgres_port (str): Postgres port.
        database_url (str | None): Optional full database URL override.
        LOG_LEVEL (str): Logging level for the application.
        SUPABASE_URL (str): Supabase API URL.
        SUPABASE_ANON_KEY (str): Supabase anon key.
        SUPABASE_SERVICE_ROLE_KEY (str): Supabase service role key.
        SUPABASE_JWT_SECRET (str): Supabase JWT secret.
        GEMINI_API_KEY (str): Gemini API key.
        OPENAI_API_KEY (str): OpenAI API key.
        CORS_ORIGIN (str): Allowed CORS origin.
        ssl_cert_url (str): URL to fetch SSL certificate.
        ssl_cert_dir (str): Directory to store SSL certs.
        ssl_cert_name (str): SSL certificate filename.
        TWILIO_ACCOUNT_SID (str): Twilio account SID.
        TWILIO_AUTH_TOKEN (str): Twilio auth token.
        TWILIO_VERIFY_SERVICE_SID (str): Twilio verify service SID.
        ENABLE_AI (bool): Toggle AI features.
        FORCE_CHEAP_MODEL (bool): Prefer cheaper LLM model when enabled.
        DEFAULT_CHEAP_MODEL (str): Default low-cost LLM model.
        DEFAULT_MODEL (str): Default primary LLM model.
        DEV_MODE_SKIP_AUTH (bool): Skip auth in development mode.
        DEV_MODE_MOCK_ADMIN_ID (UUID): Mock admin user ID for dev.
        STORE_PROMPTS (bool): Persist prompts for debugging or audits.
        DEMO_USER_EMAIL (str): Demo user email.
        DEMO_USER_PASSWORD (str): Demo user password.
        DEMO_ADMIN_EMAIL (str): Demo admin email.
        DEMO_ADMIN_PASSWORD (str): Demo admin password.
        GCP_PRIVATE_KEY_ID (str): GCP private key ID.
        GCP_PRIVATE_KEY (str): GCP private key.
        GCP_CLIENT_EMAIL (str): GCP client email.
        GCP_CLIENT_ID (str): GCP client ID.
        GCP_BUCKET (str): GCS bucket name.
        GCP_PROJECT_ID (str): GCP project ID.
        VERTEXAI_PROJECT_ID (str): Vertex AI project ID.
        VERTEXAI_LOCATION (str): Vertex AI region.
        VERTEXAI_MAX_TOKENS (int): Max tokens for Vertex AI.
        SENTRY_DSN (str | None): Sentry DSN for error reporting.
    """

    stage: Literal['dev', 'prod'] = 'dev'
    postgres_host: str = 'localhost'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'app_db'
    postgres_port: str = '5432'
    database_url: str | None = None

    LOG_LEVEL: str = 'INFO'

    SUPABASE_URL: str = 'http://127.0.0.1:54321'

    SUPABASE_ANON_KEY: str = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.'
        'CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
    )
    SUPABASE_SERVICE_ROLE_KEY: str = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.'
        'EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU'
    )
    SUPABASE_JWT_SECRET: str = 'super-secret-jwt-token-with-at-least-32-characters-long'

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
    DEFAULT_CHEAP_MODEL: str = 'gemini-2.0-flash-lite-001'
    DEFAULT_MODEL: str = 'gemini-2.5-pro'

    DEV_MODE_SKIP_AUTH: bool = True
    DEV_MODE_MOCK_ADMIN_ID: UUID = MockUserIdsEnum.ADMIN.value

    STORE_PROMPTS: bool = False

    DEMO_USER_EMAIL: str = 'mockuser@example.com'
    DEMO_USER_PASSWORD: str = 'mockuserpassword'

    DEMO_ADMIN_EMAIL: str = 'mockadmin@example.com'
    DEMO_ADMIN_PASSWORD: str = 'mockadminpassword'

    # GCP settings
    GCP_PRIVATE_KEY_ID: str = ''
    GCP_PRIVATE_KEY: str = ''
    GCP_CLIENT_EMAIL: str = ''
    GCP_CLIENT_ID: str = ''
    GCP_BUCKET: str = 'coachai-dev'
    GCP_PROJECT_ID: str = 'personio-foundation'

    # Vertex AI credentials
    VERTEXAI_PROJECT_ID: str = 'personio-foundation'
    VERTEXAI_LOCATION: str = 'europe-west9'
    VERTEXAI_MAX_TOKENS: int = 8192  # Max tokens for VertexAI in dev mode

    SENTRY_DSN: str | None = None

    @property
    def mock_user_data(self) -> MockUser:
        """Build mock demo user credentials.

        Returns:
            MockUser: Mock user account information.
        """
        return MockUser(
            email=self.DEMO_USER_EMAIL,
            password=self.DEMO_USER_PASSWORD,
            phone='+1234567890',
            full_name='Demo User',
        )

    @property
    def mock_admin_data(self) -> MockUser:
        """Build mock demo admin credentials.

        Returns:
            MockUser: Mock admin account information.
        """
        return MockUser(
            email=self.DEMO_ADMIN_EMAIL,
            password=self.DEMO_ADMIN_PASSWORD,
            phone='+1987654321',
            full_name='Admin',
        )

    model_config = SettingsConfigDict(env_file=Path(__file__).parent / '.env', extra='ignore')


settings = Settings()
