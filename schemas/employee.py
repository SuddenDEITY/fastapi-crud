from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EmployeeBase(BaseModel):
    name: str
    age: int
    role: int
    salary: int
    phone_number: str


class EmployeeUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    role: Optional[int]
    salary: Optional[int]
    phone_number: Optional[str]


class EmployeeCreate(EmployeeBase):
    ...


class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
