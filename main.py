from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
from db.config import engine
from db.models import employee
from api import employees

employee.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI little CRUD")

app.include_router(employees.router)