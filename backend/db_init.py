"""Database initialization script"""
import asyncio
from sqlalchemy import text
from app.db.session import engine, Base
from app.db.models import User
from app.core.security import get_password_hash

async def init_db():
    """Initialize database with tables and seed data"""
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Check if admin user exists
        result = await conn.execute(
            text("SELECT * FROM users WHERE email = 'admin@example.com'")
        )
        admin_exists = result.fetchone() is not None
        
        if not admin_exists:
            # Create admin user
            admin_user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("adminpassword"),
                is_active=True
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO users (email, hashed_password, is_active) 
                    VALUES (:email, :hashed_password, :is_active)
                    """
                ),
                {
                    "email": admin_user.email,
                    "hashed_password": admin_user.hashed_password,
                    "is_active": admin_user.is_active
                }
            )
            print("Admin user created")
        else:
            print("Admin user already exists")
            
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())