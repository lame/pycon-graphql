from database import db_session
from models import Department as DepartmentModel
from models import Employee as EmployeeModel
from models import Role as RoleModel
from typing import List

from sqlalchemy.orm import joinedload
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from promise import Promise
from promise.dataloader import DataLoader

lazy = lambda name: f"flask_sqlalchemy.schema.{name}"


class DepartmentQL(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node,)


# Better naming method is what it's receiving,
# but that's confusing here because all the classes are smooshed together
# class RoleQLDataLoader(DataLoader):
#     def batch_load_fn(self, role_ids):
#         # Here we return a promise that will result on the
#         # corresponding user for each key in keys
#         breakpoint()
#         employees = (
#             db_session.query(RoleModel.id, EmployeeModel)
#             .select_from(EmployeeModel)
#             .options(joinedload(EmployeeModel.role))
#             .filter(RoleModel.id.in_(role_ids))
#             .group_by(EmployeeModel.role)
#             .all()
#         )
#         print("foo")
#         # return Promise.resolve([role_employee_dict[role_id] for role_id in role_ids])


class RoleQL(SQLAlchemyObjectType):
    class Meta:
        model = RoleModel
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


class RoleConnection(relay.Connection):
    class Meta:
        node = RoleQL


class RoleByEmployeeIDDataloader(DataLoader):
    def batch_load_fn(self, employee_ids):
        breakpoint()
        roles_by_id = dict(
            db_session.query(RoleModel.id, RoleModel).filter(
                RoleModel.id.in_(employee_ids)
            )
        )
        return Promise.resolve([roles_by_id[role_id] for role_id in employee_ids])


class EmployeeQL(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node,)

    roles = relay.ConnectionField(RoleConnection)

    def resolve_roles(self, info: graphene.ResolveInfo):
        role_by_id_dataloader = RoleByEmployeeIDDataloader()
        return role_by_id_dataloader.load(self.id)


class EmployeeConnection(relay.Connection):
    class Meta:
        node = EmployeeQL


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    all_employees = SQLAlchemyConnectionField(EmployeeQL.connection)
    all_roles = SQLAlchemyConnectionField(RoleQL.connection)
    all_departments = SQLAlchemyConnectionField(DepartmentQL.connection)


schema = graphene.Schema(query=Query)
