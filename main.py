from typing import Optional, List
import asyncio 
from fastapi import FastAPI
from db.config import engine, Base
from api import employees

app = FastAPI(title="FastAPI little CRUD")

app.include_router(employees.router)

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)