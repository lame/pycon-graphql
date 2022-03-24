from database import db_session
from models import Department as DepartmentModel
from models import Employee as EmployeeModel
from models import Company as CompanyModel
from typing import List

from sqlalchemy.orm import joinedload
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from promise import Promise
from promise.dataloader import DataLoader


class CompanyQL(SQLAlchemyObjectType):
    class Meta:
        model = CompanyModel
        interfaces = (relay.Node,)

class DepartmentQL(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node,)

    # employees = relay.ConnectionField('flask_sqlalchemy.schema.EmployeeConnection')

    # def resolve_employees(self, info: graphene.ResolveInfo):
    #     def do_something_after_load(users):
    #         breakpoint()
    #         print("wow, that role has {} users")

    #     role_dataloader = RoleQLDataLoader()
    #     return role_dataloader.load(self.id).then(
    #         lambda users: do_something_after_load(users)
    #     )


class DepartmentConnection(relay.Connection):
    class Meta:
        node = DepartmentQL


# class RoleByEmployeeIDDataloader(DataLoader):
#     def batch_load_fn(self, employee_ids):
#         breakpoint()
#         roles_by_id = dict(
#             db_session.query(RoleModel.id, RoleModel).filter(
#                 RoleModel.id.in_(employee_ids)
#             )
#         )
#         return Promise.resolve([roles_by_id[role_id] for role_id in employee_ids])


class EmployeeQL(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node,)


class EmployeeConnection(relay.Connection):
    class Meta:
        node = EmployeeQL


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    companies = SQLAlchemyConnectionField(CompanyQL.connection)
    departments = SQLAlchemyConnectionField(DepartmentQL.connection)
    employees = SQLAlchemyConnectionField(EmployeeQL.connection)


schema = graphene.Schema(query=Query)
