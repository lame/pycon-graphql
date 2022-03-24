from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, Table
from sqlalchemy.orm import backref, relationship


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship(
        Company, backref="departments", uselist=False, cascade="delete,all"
    )


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship(
        Department, backref=backref("employees", uselist=True, cascade="delete,all")
    )
