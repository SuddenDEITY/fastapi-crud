from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate


def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).one_or_none()


def get_employee_by_phone_number(db: Session, phone_number: str):
    return db.query(Employee).filter(Employee.phone_number == phone_number).one_or_none()


def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: EmployeeCreate):
    db_employee = Employee(name=employee.name, age=employee.age,
                       phone_number=employee.phone_number, role=employee.role,
                       salary=employee.salary)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def put_update_employee(db: Session, employee: EmployeeCreate, employee_id: int):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).one_or_none()
    
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")

    existing_employee = get_employee_by_phone_number(db=db, phone_number=employee.phone_number)
    if existing_employee:
        raise HTTPException(status_code=403, detail="This phone number is already taken!")

    for var, value in vars(employee).items():
        setattr(db_employee, var, value) if value else None

    db_employee.modified = datetime.utcnow()
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def patch_update_employee(db: Session, employee: EmployeeUpdate, employee_id: int):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).one_or_none()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")

    existing_employee = get_employee_by_phone_number(db=db, phone_number=employee.phone_number)
    if existing_employee:
        raise HTTPException(status_code=403, detail="This phone number is already taken!")

    employee_data = employee.dict(exclude_unset=True)
    for var, value in employee_data.items():
        setattr(db_employee, var, value) if value else None

    db_employee.modified = datetime.utcnow()
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).one_or_none()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")
    db.delete(employee)
    db.commit()
    return {"ok": True}