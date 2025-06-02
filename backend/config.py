from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'

    supabase_user: str = 'postgres'
    supabase_password: str
    supabase_host: str
    supabase_port: int = 5432
    supabase_db: str = 'postgres'

    supabase_url: str
    supabase_key: str
    supabase_ssl_cert_path: str = Path(__file__).parent / 'certs' / 'prod-ca-2021.crt'

    gemini_api_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_verify_service_sid: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    test_phone_number: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
