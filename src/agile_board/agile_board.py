from psycopg import Connection

from agile_board import db

# The db stores statuses as 'Unassigned' / 'In Progress' / 'Done'.
# The API and front end use the lane ids 'backlog' / 'inprogress' / 'done'.
DB_TO_API_STATUS = {"Unassigned": "backlog", "In Progress": "inprogress", "Done": "done"}
API_TO_DB_STATUS = {v: k for k, v in DB_TO_API_STATUS.items()}


class NotFoundError(Exception):
    pass


class InvalidInputError(Exception):
    pass


# Wraps the db functions so the flask routes only deal with plain dicts.
# Row layouts come from db.py:
#   person -> (person_id, name)
#   task   -> (task_id, task_info, created_at, updated_at, status, person_id)
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

    # ---------- Dashboard ----------

    def get_summary(self) -> list[dict]:
        """Every person with their tasks. Unassigned tasks go in a final entry with personId None."""
        people = [self._person_to_dict(p) for p in db.get_all_people(self.conn)]
        tasks = [self._task_to_dict(t) for t in db.get_all_tasks(self.conn)]

        summary = []
        for person in people:
            person_tasks = [t for t in tasks if t["personId"] == person["personId"]]
            summary.append({**person, "tasks": person_tasks})

        unassigned = [t for t in tasks if t["personId"] is None]
        if unassigned:
            summary.append({"personId": None, "name": None, "tasks": unassigned})
        return summary

    # ---------- Manager ----------

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

    # ---------- Engineer ----------

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
