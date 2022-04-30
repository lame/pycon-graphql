#!/usr/bin/env python

from database import db_session, init_db, engine
from flask import Flask, g
from schema import schema
from functools import wraps
from time import sleep
from flask_graphql import GraphQLView
from query_counter import QueryCounter

# Live Demo 1
ADD_DELAY = False  # No delay per transaction
# ADD_DELAY = True  # Add 1 millisecond delay per transaction

SHOW_SQL = False

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

    engine.echo = SHOW_SQL
    if ADD_DELAY:
        engine.dialect.execution_ctx_cls.pre_exec = wrap_sleep(
            engine.dialect.execution_ctx_cls.pre_exec
        )

    app.run(port=8000)
