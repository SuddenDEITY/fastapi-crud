from fastapi import FastAPI
from api import employees
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from db.config import engine, Base
import os


app = FastAPI(title="FastAPI little CRUD")

app.include_router(employees.router)


@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# TEST DATABASE CONFIGURATION

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
test_engine = create_async_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with SessionLocal() as db:
        yield db
        await db.commit()
