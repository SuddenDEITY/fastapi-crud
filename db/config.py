from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import os

# MAIN DATABASE CONFIGURATION

MAIN_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(MAIN_DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as db:
        yield db
        await db.commit()
