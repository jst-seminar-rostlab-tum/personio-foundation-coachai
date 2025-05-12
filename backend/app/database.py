from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Dict, Any

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "db")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app_db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection() -> Dict[str, Any]:
    """
    检查数据库连接状态
    
    Returns:
        Dict[str, Any]: 包含连接状态的字典
        {
            "status": "healthy" | "unhealthy",
            "database": "connected" | "disconnected",
            "error": str (如果发生错误)
        }
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database": "connected"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        } 