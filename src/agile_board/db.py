from psycopg import Connection
from psycopg.errors import Error

# DATABASE INITIALIZATION


def init_db(conn: Connection) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute("""
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
            conn.commit()
            print("Tables Created Successfully!")
            return True
    except Error as err:
        print(f"Error in creating database tables: {err}")
        conn.rollback()
        raise


# PERSON TABLE MANIPULATION


def get_person(conn: Connection, name: str):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT person_id, name FROM person WHERE name = %s;", (name,))
            return cur.fetchone()
    except Error as err:
        print(f"Unable to get person by name '{name}': {err}")
        conn.rollback()
        raise


def get_person_by_id(conn: Connection, person_id: int):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT person_id, name FROM person WHERE person_id = %s;", (person_id,))
            return cur.fetchone()
    except Error as err:
        print(f"Unable to get person {person_id}: {err}")
        conn.rollback()
        raise


def create_person(conn: Connection, name: str) -> int:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO person (name)
                VALUES (%s)
                RETURNING person_id;
                """,
                (name,),
            )
            person_id = cur.fetchone()[0]
            conn.commit()
            return person_id
    except Error as err:
        print(f"Unable to create person: {err}")
        conn.rollback()
        raise


def delete_person_by_id(conn: Connection, person_id: int) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM person 
                WHERE person_id = %s 
                RETURNING person_id;
                """,
                (person_id,),
            )
            deleted = cur.fetchone()
            conn.commit()
            return deleted is not None
    except Error as err:
        print(f"Error deleting person {person_id}: {err}")
        conn.rollback()
        raise


# TASK TABLE MANIPULATION


def get_task_by_id(conn: Connection, task_id: int):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT task_id, task_info, created_at, updated_at, status, person_id
                FROM task
                WHERE task_id = %s;
                """,
                (task_id,),
            )
            return cur.fetchone()
    except Error as err:
        print(f"Unable to get task {task_id}: {err}")
        conn.rollback()
        raise


def create_task(conn: Connection, task_info: str) -> int:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO task (task_info)
                VALUES (%s)
                RETURNING task_id;
                """,
                (task_info,),
            )
            task_id = cur.fetchone()[0]
            conn.commit()
            return task_id
    except Error as err:
        print(f"Unable to create task: {err}")
        conn.rollback()
        raise


def delete_task(conn: Connection, task_id: int) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM task
                WHERE task_id = %s
                RETURNING task_id;
                """,
                (task_id,),
            )
            deleted = cur.fetchone()
            conn.commit()
            return deleted is not None
    except Error as err:
        print(f"Unable to delete task {task_id}: {err}")
        conn.rollback()
        raise


def get_tasks_by_status(conn: Connection, status: str):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT task_id, task_info, created_at, updated_at, status, person_id
                FROM task
                WHERE status = %s;
                """,
                (status,),
            )
            return cur.fetchall()
    except Error as err:
        print(f"Unable to retrieve tasks of {status} status: {err}")
        conn.rollback()
        raise


def get_tasks_by_person(conn: Connection, person_id: int):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT task_id, task_info, created_at, updated_at, status, person_id
                FROM task
                WHERE person_id = %s;
                """,
                (person_id,),
            )
            return cur.fetchall()
    except Error as err:
        print(f"Unable to retrieve tasks for person {person_id}: {err}")
        conn.rollback()
        raise


def get_all_people(conn: Connection):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT person_id, name FROM person ORDER BY name;")
            return cur.fetchall()
    except Error as err:
        print(f"Unable to retrieve people: {err}")
        conn.rollback()
        raise


def get_all_tasks(conn: Connection):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT task_id, task_info, created_at, updated_at, status, person_id
                FROM task
                ORDER BY task_id;
                """
            )
            return cur.fetchall()
    except Error as err:
        print(f"Unable to retrieve tasks: {err}")
        conn.rollback()
        raise


def assign_task(conn: Connection, task_id: int, person_id: int) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE task
                SET person_id = %s, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = %s
                RETURNING task_id;
                """,
                (person_id, task_id),
            )
            updated = cur.fetchone()
            conn.commit()
            return updated is not None
    except Error as err:
        print(f"Unable to assign task {task_id} to person {person_id}: {err}")
        conn.rollback()
        raise


def update_task_status(conn: Connection, task_id: int, status: str) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE task
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = %s
                RETURNING task_id;
                """,
                (status, task_id),
            )
            updated = cur.fetchone()
            conn.commit()
            return updated is not None
    except Error as err:
        print(f"Unable to update task {task_id} to {status}: {err}")
        conn.rollback()
        raise
