from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from db.models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate


async def get_employee(db: AsyncSession, employee_id: int):
    query = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_employee_by_phone_number(db: AsyncSession, phone_number: str):
    query = select(Employee).where(Employee.phone_number == phone_number)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_employees(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(Employee).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_employee(db: AsyncSession, employee: EmployeeCreate):
    db_employee = Employee(
        name=employee.name,
        age=employee.age,
        phone_number=employee.phone_number,
        role=employee.role,
        salary=employee.salary,
    )
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def put_update_employee(
    db: AsyncSession, employee: EmployeeCreate, employee_id: int
):
    db_employee = await get_employee(db=db, employee_id=employee_id)

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")

    existing_employee = await get_employee_by_phone_number(
        db=db, phone_number=employee.phone_number
    )
    if existing_employee:
        raise HTTPException(
            status_code=403, detail="This phone number is already taken!"
        )

    for var, value in vars(employee).items():
        setattr(db_employee, var, value) if value is not None else None

    db_employee.updated_at = datetime.utcnow()
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def patch_update_employee(
    db: AsyncSession, employee: EmployeeUpdate, employee_id: int
):
    db_employee = await get_employee(db=db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")

    existing_employee = await get_employee_by_phone_number(
        db=db, phone_number=employee.phone_number
    )
    if existing_employee:
        raise HTTPException(
            status_code=403, detail="This phone number is already taken!"
        )

    employee_data = employee.dict(exclude_unset=True)
    for var, value in employee_data.items():
        setattr(db_employee, var, value) if value is not None else None

    db_employee.updated_at = datetime.utcnow()
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def delete_employee(db: AsyncSession, employee_id: int):
    employee = await get_employee(db=db, employee_id=employee_id)
    print(employee)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")
    await db.delete(employee)
    await db.commit()
    return {"ok": True}
