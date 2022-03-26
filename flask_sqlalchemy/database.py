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
    from models import Department, Employee, Company

    fake = Faker()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Create the fixtures
    companies = [Company(name=fake.company()) for _ in range(100)]
    departments = [
        Department(name=fake.job(), company=sample(companies, 1)[0]) for _ in range(200)
    ]

    employees = [
        Employee(
            name=fake.name(),
            department=sample(departments, 1)[0],
        )
        for _ in range(10_000)
    ]

    db_session.add_all(companies + departments + employees)
    db_session.commit()
