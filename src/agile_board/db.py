from psycopg import Connection

TASK_COLUMNS = "task_id, task_info, created_at, updated_at, status, person_id"


def _fetch_one(conn: Connection, sql: str, params: tuple = ()):
    with conn.transaction():
        return conn.execute(sql, params).fetchone()


def _fetch_all(conn: Connection, sql: str, params: tuple = ()):
    with conn.transaction():
        return conn.execute(sql, params).fetchall()


def init_db(conn: Connection) -> bool:
    with conn.transaction():
        conn.execute("""
            CREATE TABLE IF NOT EXISTS person (
                person_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR(50) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task (
                task_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                task_info TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'Unassigned' CHECK (status IN ('Unassigned', 'In Progress', 'Done')),
                person_id INT REFERENCES person(person_id) ON DELETE SET NULL
            );
        """)
    return True


def get_person(conn: Connection, name: str):
    return _fetch_one(conn, "SELECT person_id, name FROM person WHERE name = %s", (name,))


def get_person_by_id(conn: Connection, person_id: int):
    return _fetch_one(conn, "SELECT person_id, name FROM person WHERE person_id = %s", (person_id,))


def get_all_people(conn: Connection):
    return _fetch_all(conn, "SELECT person_id, name FROM person ORDER BY name ASC")


def create_person(conn: Connection, name: str) -> int:
    return _fetch_one(conn, "INSERT INTO person (name) VALUES (%s) RETURNING person_id", (name,))[0]


def update_person_name(conn: Connection, person_id: int, new_name: str) -> bool:
    sql = "UPDATE person SET name = %s WHERE person_id = %s RETURNING person_id"
    return _fetch_one(conn, sql, (new_name, person_id)) is not None


def delete_person_by_id(conn: Connection, person_id: int) -> bool:
    return _fetch_one(conn, "DELETE FROM person WHERE person_id = %s RETURNING person_id", (person_id,)) is not None


def get_task_by_id(conn: Connection, task_id: int):
    return _fetch_one(conn, f"SELECT {TASK_COLUMNS} FROM task WHERE task_id = %s", (task_id,))


def get_tasks_by_status(conn: Connection, status: str):
    return _fetch_all(conn, f"SELECT {TASK_COLUMNS} FROM task WHERE status = %s", (status,))


def get_tasks_by_person(conn: Connection, person_id: int):
    return _fetch_all(conn, f"SELECT {TASK_COLUMNS} FROM task WHERE person_id = %s", (person_id,))


def get_all_tasks(conn: Connection):
    return _fetch_all(conn, f"SELECT {TASK_COLUMNS} FROM task ORDER BY created_at DESC")


def create_task(conn: Connection, task_info: str) -> int:
    return _fetch_one(conn, "INSERT INTO task (task_info) VALUES (%s) RETURNING task_id", (task_info,))[0]


def assign_task(conn: Connection, task_id: int, person_id: int | None) -> bool:
    sql = "UPDATE task SET person_id = %s, updated_at = CURRENT_TIMESTAMP WHERE task_id = %s RETURNING task_id"
    return _fetch_one(conn, sql, (person_id, task_id)) is not None


def update_task_status(conn: Connection, task_id: int, status: str) -> bool:
    sql = "UPDATE task SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE task_id = %s RETURNING task_id"
    return _fetch_one(conn, sql, (status, task_id)) is not None


def delete_task(conn: Connection, task_id: int) -> bool:
    return _fetch_one(conn, "DELETE FROM task WHERE task_id = %s RETURNING task_id", (task_id,)) is not None
