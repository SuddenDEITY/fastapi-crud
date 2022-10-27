import enum
from zoneinfo import available_timezones
from sqlalchemy.orm import validates
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, Text
from fastapi import HTTPException
from ..config import Base
from .mixins import Timestamp


class Role(enum.IntEnum):
    developer = 1
    lead = 2
    qa = 3
    manager = 4


class Employee(Timestamp, Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    phone_number = Column(String(25), unique=True, index=True, nullable=False)
    age = Column(Integer, index=True, nullable=False)
    salary = Column(Integer, index=True, nullable=False)
    role = Column(Enum(Role))

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if '+' not in value:
            raise HTTPException(status_code=400, detail="Phone number must contain '+' ")
        return value
    
    @validates('role')
    def validate_role(self, key, value):
        available_roles = [role.value for role in Role]
        if value not in available_roles:
             raise HTTPException(status_code=400, detail=f"Invalid role! Available roles: {available_roles}")
        return value
    
    

