from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from random import sample
from faker import Faker


engine = create_engine("sqlite:///database.sqlite3", convert_unicode=True)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models import Department, Employee, Role

    print("INIT DB")

    fake = Faker()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create the fixtures
    departments = [Department(name=fake.job()) for _ in range(20)]

    role_names = [
        "manager",
        "engineer",
        "designer",
        "foo",
        "bar",
        "baz",
        "i lack creativity",
    ]
    roles = [Role(name=role_name) for role_name in role_names]

    employees = [
        Employee(
            name=fake.name(),
            department=sample(departments, 1)[0],
            roles=sample(roles, 5),
        )
        for _ in range(1_000)
    ]

    db_session.add_all(departments + roles + employees)
    db_session.commit()
