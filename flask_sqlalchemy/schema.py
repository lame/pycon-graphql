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

USE_DATALOADERS = True

resolver_counter, department_dataloader_counter, employee_dataloader_counter = 1, 1, 1

class EmployeeDataLoader(DataLoader):
    def batch_load_fn(self, department_ids) -> Promise:

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
        global department_dataloader_counter
        print(f"Dataloader Count: {department_dataloader_counter}")
        department_dataloader_counter += 1

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

        if USE_DATALOADERS:
            return employee_dataloader.load(department.id)

        return department.employees


class CompanyQL(SQLAlchemyObjectType):
    class Meta:
        model = CompanyModel
        interfaces = (relay.Node,)

    departments = graphene.ConnectionField(DepartmentQL.connection)

    def resolve_departments(company, info: graphene.ResolveInfo) -> Promise:
        global resolver_counter
        print(f"Resolver Count: {resolver_counter}")
        resolver_counter += 1

        if USE_DATALOADERS:
            return department_dataloader.load(company.id)
        return company.departments

class RootQuery(graphene.ObjectType):
    node = relay.Node.Field()

    companies = SQLAlchemyConnectionField(CompanyQL.connection)
    departments = SQLAlchemyConnectionField(DepartmentQL.connection)
    employees = SQLAlchemyConnectionField(EmployeeQL.connection)


schema = graphene.Schema(query=RootQuery)


# class UserLoader(DataLoader):
#     async def batch_load_fn(self, keys):
#         return await my_batch_get_users(keys)

# user_loader = UserLoader()
# class User(graphene.ObjectType):
#     name = graphene.String()
#     best_friend = graphene.Field(lambda: User)
#     friends = graphene.List(lambda: User)

#     def resolve_best_friend(self, args, context, info):
#         return user_loader.load(self.best_friend_id)

#     def resolve_friends(self, args, context, info):
#         return user_loader.load_many(self.friend_ids)
