from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'

    supabase_environment: Literal['local', 'remote'] = 'remote'
    supabase_project_id: str | None = None
    supabase_password: str = ''
    supabase_port: int = 5432
    supabase_db: str = 'postgres'
    supabase_user: str = 'postgres'

    supabase_key: str
    supabase_ssl_cert_path: str = str(Path(__file__).parent / 'certs' / 'prod-ca-2021.crt')

    gemini_api_key: str = ''
    twilio_account_sid: str = ''
    twilio_auth_token: str = ''
    twilio_verify_service_sid: str | None = None
    twilio_phone_number: str | None = None
    test_phone_number: str | None = None

    ENABLE_AI: bool = False
    FORCE_CHEAP_MODEL: bool = True

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
