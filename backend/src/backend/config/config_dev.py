from .config import BaseConfig


class DevConfig(BaseConfig):
    stage = "dev"
    POSTGRES_SERVER = "localhost"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_DB = "app_db"
    POSTGRES_PORT = "5432"
