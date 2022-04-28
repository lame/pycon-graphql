# Set up Root dir
import os
import sys
root = os.path.abspath(
    os.path.join(
        os.path.curdir, './flask_sqlalchemy/'
    )
)
sys.path.append(root)

# Import db stuff
from database import Base, init_db
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import backref, relationship

# Initialize the db schema and stuff
init_db()


class Company:
    pass
class Department:
    pass
class Employee:
    pass

class CompanyModel(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class DepartmentModel(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    company_id = Column(
        Integer,
        ForeignKey("companies.id")
    )
    company = relationship(
        Company,
        backref="departments",
        uselist=False,
        cascade="delete,all"
    )

class EmployeeModel(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(
        Integer,
        ForeignKey("departments.id")
    )
    department = relationship(
        Department,
        backref=backref(
            "employees",
            uselist=True,
            cascade="delete,all"
        )
    )


from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType

class CompanyQL(SQLAlchemyObjectType):
    class Meta:
        # The model SQLA maps to node
        model = CompanyModel
        interfaces = (relay.Node,)  # Object state


class DepartmentQL(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node,)


class EmployeeQL(SQLAlchemyObjectType):
    class Meta:
        model = EmployeeModel
        interfaces = (relay.Node,)


import graphene
from graphene_sqlalchemy import \
    SQLAlchemyConnectionField

# Create the root node
class RootQuery(graphene.ObjectType):
    node = relay.Node.Field()

    companies = (
        SQLAlchemyConnectionField(
            CompanyQL.connection
        )
    )
    departments = (
        SQLAlchemyConnectionField(
            DepartmentQL.connection
        )
    )
    employees = (
        SQLAlchemyConnectionField(
            EmployeeQL.connection
        )
    )

from flask import Flask
from flask_graphql import GraphQLView

# Make the root node discoverable
schema = graphene.Schema(query=RootQuery)

app = Flask(__name__)
app.debug = True


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,  # Our schema
        graphiql=True
    )
)

from database import db_session

companies = db_session.query(Company).all()
query_count = 1

for company in companies:
    query_count += 1
    departments = (
        db_session.query(Department)
        .filter_by(company_id=company.id)
        .all()
    )
    for department in departments:
        query_count += 1
        employees = (
            db_session.query(Employee)
            .filter_by(
                department_id=department.id
            ).all()
        )

print(query_count) # What do you think it'll be?!

from collections import defaultdict
from promise import Promise
from promise.dataloader import DataLoader

class DepartmentDataLoader(DataLoader):
    def batch_load_fn(self, company_ids) -> Promise:
        departments_by_company_id = defaultdict(list)
        department_instances = (
            db_session.query(DepartmentModel)
            .filter(
                DepartmentModel.company_id.in_(
                    company_ids
                )
            ).all()
        )
        for department in department_instances:
            departments_by_company_id[
                department.company_id
            ].append(department)

        # Need to return in same order as company_ids
        return Promise.resolve(
            [
                departments_by_company_id[company_id]
                for company_id in company_ids
            ]
        )


# TODO: Pretend you know more about this and
#       it's just really intuitive
from promise import Promise

def _resolve(call):
    pass

# Taken from Promise docs
# https://github.com/syrusakbary/promise#usage
my_promise = Promise(
    lambda resolver,
    rejector: _resolve(resolver)
)
my_promise = my_promise.resolve('Bub')
print(f'B. L. Z. {my_promise.get()}')
# >> B. L. Z. Bub
print(f'I am Fulfilled {my_promise.is_fulfilled}')
# >> Fulfilled True



# See... super simple

promise = Promise(
    executor=baz_resolve,
    scheduler=baz_reject
)
promise.reject(
    ValueError("Wasn't feeling it")
    )



import promise
from promise.dataloader import DataLoader

class DepartmentDataLoader(DataLoader):
    def batch_load_fn(self, company_ids) -> Promise:
        # company_ids is an unordered list

        departments_by_company_id = \
            defaultdict(list)
        departments = (
            db_session.query(DepartmentModel)
            .filter(DepartmentModel.company_id.in_(company_ids))
            .all()
        )
        for department in departments:
            departments_by_company_id[department.company_id].append(department)

        # Need to return in same order as company_ids
        return Promise.resolve(
            [departments_by_company_id[company_id] for company_id in company_ids]
        )








