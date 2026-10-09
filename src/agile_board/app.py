import os

from dotenv import load_dotenv
from flask import Flask, current_app, render_template
from flask import g as req_cache
from psycopg_pool import ConnectionPool

from agile_board import db
from agile_board.agile_board import AgileBoard


def get_db():
    if "db_conn" not in req_cache:
        req_cache.db_conn = current_app.pool.getconn()
    return req_cache.db_conn


def close_db(exc=None):
    conn = req_cache.pop("db_conn", None)
    if conn is not None:
        current_app.pool.putconn(conn)


def create_app():
    app = Flask(__name__)
    load_dotenv()

    DB_URL = os.getenv("DB_URL")
    if not DB_URL:
        raise RuntimeError("Environment Error: DB_URL env var not set")

    app.pool = ConnectionPool(conninfo=DB_URL, open=True)

    with app.pool.connection() as conn:
        db.init_db(conn)

    app.teardown_appcontext(close_db)

    @app.route("/")
    def index_page():
        return render_template("index.html")

    @app.route("/manager")
    def manager_view():
        return render_template("manager.html")

    @app.route("/engineer/<name>")
    def engineer_view(name):
        return render_template("engineer.html", name=name)

    @app.route("/api/summary_json", methods=(["GET"]))
    def whole_summary():
        return AgileBoard(get_db()).get_summary()

    @app.route("/api/task/", methods=(["POST"]))
    def create_task():
        return {"name": "John Doe", "tasks": ["Task 1", "Task 2"]}

    @app.route("/api/task/<task_Id>/assign", methods=(["POST"]))
    def assign_task():
        return {"name": "John Doe", "tasks": ["Task 1", "Task 2"]}

    @app.route("/api/task/<task_Id>/<person_Id>/inprogress", methods=(["POST"]))
    def update_task_in_progress():
        return {"name": "John Doe", "tasks": ["Task 1", "Task 2"]}

    @app.route("/api/task/<task_Id>/<person_Id>/done", methods=(["POST"]))
    def update_task_done():
        return {"name": "John Doe", "tasks": ["Task 1", "Task 2"]}

    @app.route("/api/people/<people_Id>", methods=(["POST"]))
    def create_person():
        return {"name": "John Doe", "tasks": ["Task 1", "Task 2"]}

    return app
