from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod'] = 'dev'

    supabase_environment: Literal['local', 'remote'] = 'local'
    supabase_project_id: str | None = None
    supabase_password: str = Field('', alias='SUPABASE_PASSWORD')
    supabase_port: int = Field(5432, alias='SUPABASE_PORT')
    supabase_db: str = Field('postgres', alias='SUPABASE_DB')
    supabase_user: str = Field('postgres', alias='SUPABASE_USER')
    supabase_host: str = Field('127.0.0.1', alias='SUPABASE_HOST')

    supabase_anon_key: str = Field(..., alias='SUPABASE_ANON_KEY')
    supabase_ssl_cert_path: str = str(Path(__file__).parent / 'certs' / 'prod-ca-2021.crt')

    gemini_api_key: str = Field('', alias='GEMINI_API_KEY')
    twilio_account_sid: str = Field('', alias='TWILIO_ACCOUNT_SID')
    twilio_auth_token: str = Field('', alias='TWILIO_AUTH_TOKEN')
    twilio_verify_service_sid: str | None = Field(None, alias='TWILIO_VERIFY_SERVICE_SID')
    twilio_phone_number: str | None = Field(None, alias='TWILIO_PHONE_NUMBER')
    test_phone_number: str | None = Field(None, alias='TEST_PHONE_NUMBER')

    ENABLE_AI: bool = Field(False, alias='ENABLE_AI')
    FORCE_CHEAP_MODEL: bool = Field(True, alias='FORCE_CHEAP_MODEL')

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
