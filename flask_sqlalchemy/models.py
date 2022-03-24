from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, Table
from sqlalchemy.orm import backref, relationship


class Department(Base):
    __tablename__ = "department"
    id = Column(Integer, primary_key=True)
    name = Column(String)


association_table = Table(
    "association",
    Base.metadata,
    Column("employee_id", ForeignKey("employee.id")),
    Column("role_id", ForeignKey("roles.id")),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    hired_on = Column(DateTime, default=func.now())
    department_id = Column(Integer, ForeignKey("department.id"))
    # Use cascade='delete,all' to propagate the deletion of a Department onto its Employees
    department = relationship(
        Department, backref=backref("employees", uselist=True, cascade="delete,all")
    )
    roles = relationship(Role, secondary=association_table)
