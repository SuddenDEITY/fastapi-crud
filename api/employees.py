from typing import List
import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.config import get_db
from schemas.employee import EmployeeCreate, Employee, EmployeeUpdate
from api.utils.employees import (
    get_employee,
    get_employee_by_phone_number,
    get_employees,
    create_employee,
    put_update_employee,
    patch_update_employee,
    delete_employee,
)

router = fastapi.APIRouter()


@router.get("/employees", response_model=List[Employee])
async def read_employees(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
):
    employees = await get_employees(db=db, skip=skip, limit=limit)
    return employees


@router.post("/employees", response_model=Employee, status_code=201)
async def create_new_employee(
    employee: EmployeeCreate, db: AsyncSession = Depends(get_db)
):
    db_employee = await get_employee_by_phone_number(
        db=db, phone_number=employee.phone_number
    )
    if db_employee:
        raise HTTPException(
            status_code=403, detail="Phone number is already registered"
        )
    result = await create_employee(db=db, employee=employee)
    return result


@router.put("/employees/{employee_id}", response_model=Employee, status_code=200)
async def full_update_employee(
    employee_id: int, employee: EmployeeCreate, db: AsyncSession = Depends(get_db)
):
    db_employee = await put_update_employee(
        db=db, employee_id=employee_id, employee=employee
    )
    return db_employee


@router.patch("/employees/{employee_id}", response_model=Employee, status_code=200)
async def partial_update_employee(
    employee_id: int, employee: EmployeeUpdate, db: AsyncSession = Depends(get_db)
):
    db_employee = await patch_update_employee(
        db=db, employee_id=employee_id, employee=employee
    )
    return db_employee


@router.get("/employees/{employee_id}", response_model=Employee)
async def read_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    db_employee = await get_employee(db=db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee


@router.delete("/employees/{employee_id}")
async def remove_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_employee(db=db, employee_id=employee_id)
    return result
