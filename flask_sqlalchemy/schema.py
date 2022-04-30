# from aiodataloader import DataLoader
from collections import defaultdict

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from promise import Promise
from promise.dataloader import DataLoader

from database import db_session
from models import Company as CompanyModel
from models import Department as DepartmentModel
from models import Employee as EmployeeModel

# Live Demo 2
USE_DATALOADERS = False
# USE_DATALOADERS = True


department_resolver_counter, employee_resolver_counter, department_dataloader_counter, employee_dataloader_counter = 0, 0, 0, 0

class EmployeeDataLoader(DataLoader):
    def batch_load_fn(self, department_ids) -> Promise:
        global employee_resolver_counter
        global employee_dataloader_counter
        employee_dataloader_counter += 1
        print(f"Employee Resolver Count: {employee_resolver_counter}")
        print(f"Employee Dataloader Count: {employee_dataloader_counter}")
        employees_by_department_id = defaultdict(list)
        employees = (
            db_session.query(EmployeeModel)
            .filter(EmployeeModel.department_id.in_(department_ids))
            .all()
        )
        for employee in employees:
            employees_by_department_id[employee.department_id].append(employee)
        return Promise.resolve(
            [employees_by_department_id[department_id] for department_id in department_ids]
        )

class DepartmentDataLoader(DataLoader):
    def batch_load_fn(self, company_ids) -> Promise:
        global department_resolver_counter
        global department_dataloader_counter
        department_dataloader_counter += 1
        print(f"Department Resolver Count: {department_resolver_counter}")
        print(f"Department Dataloader Count: {department_dataloader_counter}")

        departments_by_company_id = defaultdict(list)
        departments = (
            db_session.query(DepartmentModel)
            .filter(DepartmentModel.company_id.in_(company_ids))
            .all()
        )
        for department in departments:
            departments_by_company_id[department.company_id].append(department)
        return Promise.resolve(
            [departments_by_company_id[company_id] for company_id in company_ids]
        )


department_dataloader = DepartmentDataLoader()
employee_dataloader = EmployeeDataLoader()


class EmployeeQL(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node,)


class DepartmentQL(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node,)

    employees = graphene.ConnectionField(EmployeeQL.connection)

    def resolve_employees(department, info: graphene.ResolveInfo) -> Promise:
        global employee_resolver_counter
        employee_resolver_counter += 1
        if USE_DATALOADERS:
            return employee_dataloader.load(department.id)
        else:
            print(f'Employee Resolver Count: {employee_resolver_counter}')
            return department.employees


class CompanyQL(SQLAlchemyObjectType):
    class Meta:
        model = CompanyModel
        interfaces = (relay.Node,)

    departments = graphene.ConnectionField(DepartmentQL.connection)


    def resolve_departments(company, info: graphene.ResolveInfo) -> Promise:
        global department_resolver_counter
        department_resolver_counter += 1

        if USE_DATALOADERS:
            return department_dataloader.load(company.id)
        else:
            print(f'Department Resolver Count: {department_resolver_counter}')
            return company.departments

class RootQuery(graphene.ObjectType):
    node = relay.Node.Field()

    companies = SQLAlchemyConnectionField(CompanyQL.connection)
    departments = SQLAlchemyConnectionField(DepartmentQL.connection)
    employees = SQLAlchemyConnectionField(EmployeeQL.connection)


schema = graphene.Schema(query=RootQuery)
