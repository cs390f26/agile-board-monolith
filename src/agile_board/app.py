import atexit
import os

from dotenv import load_dotenv
from flask import Flask, abort, current_app, render_template, request
from flask import g as req_cache
from psycopg_pool import ConnectionPool

from agile_board import db
from agile_board.agile_board import AgileBoard, InvalidInputError, NotFoundError


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
    atexit.register(app.pool.close)

    @app.route("/")
    def index_page():
        return render_template("index.html")

    @app.route("/manager")
    def manager_view():
        return render_template("manager.html")

    @app.route("/engineer/<int:person_id>")
    def engineer_view(person_id):
        try:
            person = AgileBoard(get_db()).get_person(person_id)
        except NotFoundError:
            abort(404)
        return render_template("engineer.html", person_id=person_id, name=person["name"])

    @app.route("/api/summary_json", methods=(["GET"]))
    def whole_summary():
        return AgileBoard(get_db()).get_summary()

    @app.route("/api/people/<person_id>/tasks", methods=(["GET"]))
    def engineer_summary(person_id):
        return AgileBoard(get_db()).get_engineer_tasks(person_id)

    @app.route("/api/task/", methods=(["POST"]))
    def create_task():
        body = request.get_json(silent=True) or {}
        return AgileBoard(get_db()).create_task(body.get("title")), 201

    @app.route("/api/task/<int:task_id>/assign", methods=(["POST"]))
    def assign_task(task_id):
        body = request.get_json(silent=True) or {}
        try:
            person_id = int(body.get("person_id"))
        except (TypeError, ValueError):
            raise InvalidInputError("person_id must be an integer")
        return AgileBoard(get_db()).assign_task(task_id, person_id)

    @app.route("/api/task/<int:task_id>/<int:person_id>/inprogress", methods=(["POST"]))
    def update_task_in_progress(task_id, person_id):
        return AgileBoard(get_db()).move_task(task_id, "inprogress")

    @app.route("/api/task/<int:task_id>/<int:person_id>/done", methods=(["POST"]))
    def update_task_done(task_id, person_id):
        return AgileBoard(get_db()).move_task(task_id, "done")

    @app.route("/api/people", methods=(["POST"]))
    def create_person():
        body = request.get_json(silent=True) or {}
        return AgileBoard(get_db()).create_person(body.get("name")), 201

    @app.errorhandler(InvalidInputError)
    def handle_invalid_input(err):
        return {"error": str(err)}, 400

    @app.errorhandler(NotFoundError)
    def handle_not_found(err):
        return {"error": str(err)}, 404

    return app
