# from aiodataloader import DataLoader
from database import db_session
from models import Department as DepartmentModel
from models import Employee as EmployeeModel
from models import Company as CompanyModel
from collections import defaultdict

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from promise import Promise
from promise.dataloader import DataLoader

resolver_counter, dataloader_counter = 1, 1


class DepartmentQL(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node,)


class DepartmentDataLoader(DataLoader):
    def batch_load_fn(self, company_ids) -> Promise:
        global dataloader_counter
        print(f"Dataloader Count: {dataloader_counter}")
        dataloader_counter += 1

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


class CompanyQL(SQLAlchemyObjectType):
    class Meta:
        model = CompanyModel
        interfaces = (relay.Node,)

    departments = graphene.ConnectionField(DepartmentQL.connection)

    def resolve_departments(self, info: graphene.ResolveInfo) -> Promise:
        global resolver_counter
        print(f"Resolver Count: {resolver_counter}")
        resolver_counter += 1

        return department_dataloader.load(self.id)


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
