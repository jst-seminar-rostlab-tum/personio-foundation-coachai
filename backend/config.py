from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod']
    postgres_host: str = 'https://db.qgqfapwoopmzrkartwfw.supabase.co'
    postgres_user: str = 'postgres'
    # postgres_password: str = 'postgres'
    postgres_password: str = 'vunran-6poswo-gImxos'
    postgres_db: str = 'postgres'
    postgres_port: str = '5432'

    model_config = SettingsConfigDict(env_file='.env.example', extra='ignore')


settings = Settings()
