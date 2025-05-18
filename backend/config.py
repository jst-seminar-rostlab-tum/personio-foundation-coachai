from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stage: Literal['dev', 'prod']
    postgres_host: str = 'localhost'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_db: str = 'app_db'
    postgres_port: str = '5432'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()

# testing comment
