#!/usr/bin/env python

from database import db_session, init_db, engine
from flask import Flask
from schema import schema
from functools import wraps
from time import sleep
from flask_graphql import GraphQLView

ADD_DELAY = True
DEBUG = False

app = Flask(__name__)
app.debug = True


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def wrap_sleep(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # print("simulated delay")
        sleep(0.001)
        return func(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    init_db()

    engine.echo = DEBUG
    if ADD_DELAY:
        engine.dialect.execution_ctx_cls.pre_exec = wrap_sleep(
            engine.dialect.execution_ctx_cls.pre_exec
        )

    app.run(port=8000)
