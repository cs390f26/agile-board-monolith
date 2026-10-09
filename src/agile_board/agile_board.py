from collections import defaultdict

from psycopg import Connection

from agile_board import db

DB_TO_API_STATUS = {"Unassigned": "backlog", "In Progress": "inprogress", "Done": "done"}
API_TO_DB_STATUS = {v: k for k, v in DB_TO_API_STATUS.items()}


class NotFoundError(Exception):
    pass


class InvalidInputError(Exception):
    pass


class AgileBoard:
    def __init__(self, conn: Connection):
        self.conn = conn

    @staticmethod
    def _person_to_dict(row) -> dict:
        return {"personId": row[0], "name": row[1]}

    @staticmethod
    def _task_to_dict(row) -> dict:
        return {
            "taskId": row[0],
            "title": row[1],
            "status": DB_TO_API_STATUS.get(row[4], "backlog"),
            "personId": row[5],
        }

    def get_summary(self) -> list[dict]:
        tasks_by_person = defaultdict(list)
        for row in db.get_all_tasks(self.conn):
            task = self._task_to_dict(row)
            tasks_by_person[task["personId"]].append(task)

        summary = [{**person, "tasks": tasks_by_person[person["personId"]]} for person in self.get_people()]
        if tasks_by_person[None]:
            summary.append({"personId": None, "name": None, "tasks": tasks_by_person[None]})
        return summary

    def get_people(self) -> list[dict]:
        return [self._person_to_dict(p) for p in db.get_all_people(self.conn)]

    def create_person(self, name: str) -> dict:
        name = (name or "").strip()
        if not name:
            raise InvalidInputError("name is required")
        if db.get_person(self.conn, name) is not None:
            raise InvalidInputError(f"person '{name}' already exists")
        person_id = db.create_person(self.conn, name)
        return {"personId": person_id, "name": name}

    def create_task(self, title: str) -> dict:
        title = (title or "").strip()
        if not title:
            raise InvalidInputError("title is required")
        task_id = db.create_task(self.conn, title)
        return self._task_to_dict(db.get_task_by_id(self.conn, task_id))

    def assign_task(self, task_id: int, person_id: int) -> dict:
        if db.get_person_by_id(self.conn, person_id) is None:
            raise NotFoundError(f"person {person_id} not found")
        if not db.assign_task(self.conn, task_id, person_id):
            raise NotFoundError(f"task {task_id} not found")
        return self._task_to_dict(db.get_task_by_id(self.conn, task_id))

    def get_engineer_tasks(self, name: str) -> list[dict]:
        person = db.get_person(self.conn, name)
        if person is None:
            raise NotFoundError(f"engineer '{name}' not found")
        return [self._task_to_dict(t) for t in db.get_tasks_by_person(self.conn, person[0])]

    def move_task(self, task_id: int, status: str) -> dict:
        if status not in API_TO_DB_STATUS:
            raise InvalidInputError(f"invalid status '{status}'")
        if not db.update_task_status(self.conn, task_id, API_TO_DB_STATUS[status]):
            raise NotFoundError(f"task {task_id} not found")
        return self._task_to_dict(db.get_task_by_id(self.conn, task_id))
