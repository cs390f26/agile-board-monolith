import pytest
from psycopg.errors import CheckViolation

from agile_board import db

# ---------- DATABASE INITIALIZATION ----------


def test_init_db(db_conn):
    assert db.init_db(db_conn) is True


# PERSON TABLE TESTS


def test_create_and_get_person(db_conn):
    person_id = db.create_person(db_conn, "Alice")
    assert isinstance(person_id, int)

    person = db.get_person_by_id(db_conn, person_id)
    assert person == (person_id, "Alice")

    person_by_name = db.get_person(db_conn, "Alice")
    assert person_by_name == (person_id, "Alice")


def test_get_person_not_found(db_conn):
    assert db.get_person_by_id(db_conn, 999) is None
    assert db.get_person(db_conn, "Nonexistent") is None


def test_get_all_people_ordered(db_conn):
    db.create_person(db_conn, "Charlie")
    db.create_person(db_conn, "Alice")
    db.create_person(db_conn, "Bob")

    people = db.get_all_people(db_conn)
    names = [name for _, name in people]

    # Verify alphabetical ordering (ORDER BY name ASC)
    assert names == ["Alice", "Bob", "Charlie"]


def test_update_person_name(db_conn):
    person_id = db.create_person(db_conn, "Old Name")

    success = db.update_person_name(db_conn, person_id, "New Name")
    assert success is True

    updated_person = db.get_person_by_id(db_conn, person_id)
    assert updated_person[1] == "New Name"


def test_update_person_not_found(db_conn):
    assert db.update_person_name(db_conn, 999, "Name") is False


def test_delete_person_by_id(db_conn):
    person_id = db.create_person(db_conn, "Dave")

    assert db.delete_person_by_id(db_conn, person_id) is True
    assert db.get_person_by_id(db_conn, person_id) is None


def test_delete_person_not_found(db_conn):
    assert db.delete_person_by_id(db_conn, 999) is False


# ---------- TASK TABLE TESTS ----------


def test_create_and_get_task(db_conn):
    task_id = db.create_task(db_conn, "Write unit tests")
    assert isinstance(task_id, int)

    task = db.get_task_id(db_conn, task_id) if hasattr(db, "get_task_id") else db.get_task_by_id(db_conn, task_id)

    assert task[0] == task_id
    assert task[1] == "Write unit tests"
    assert task[4] == "Unassigned"  # Default status
    assert task[5] is None  # Default person_id


def test_get_task_not_found(db_conn):
    assert db.get_task_by_id(db_conn, 999) is None


def test_assign_task(db_conn):
    person_id = db.create_person(db_conn, "Eve")
    task_id = db.create_task(db_conn, "Build API")

    # Assign task to person
    assert db.assign_task(db_conn, task_id, person_id) is True
    task = db.get_task_by_id(db_conn, task_id)
    assert task[5] == person_id

    # Unassign task (set person_id to None)
    assert db.assign_task(db_conn, task_id, None) is True
    task = db.get_task_by_id(db_conn, task_id)
    assert task[5] is None


def test_get_tasks_by_person(db_conn):
    person1_id = db.create_person(db_conn, "Frank")
    person2_id = db.create_person(db_conn, "Grace")

    t1 = db.create_task(db_conn, "Task 1")
    t2 = db.create_task(db_conn, "Task 2")

    db.assign_task(db_conn, t1, person1_id)
    db.assign_task(db_conn, t2, person2_id)

    tasks_frank = db.get_tasks_by_person(db_conn, person1_id)
    assert len(tasks_frank) == 1
    assert tasks_frank[0][0] == t1


def test_update_task_status(db_conn):
    task_id = db.create_task(db_conn, "Fix bug")

    assert db.update_task_status(db_conn, task_id, "In Progress") is True
    task = db.get_task_by_id(db_conn, task_id)
    assert task[4] == "In Progress"

    assert db.update_task_status(db_conn, task_id, "Done") is True
    task = db.get_task_by_id(db_conn, task_id)
    assert task[4] == "Done"


def test_update_task_status_invalid_check_constraint(db_conn):
    task_id = db.create_task(db_conn, "Invalid status test")

    # 'Archived' violates CHECK constraint (status IN ('Unassigned', 'In Progress', 'Done'))
    with pytest.raises(CheckViolation):
        db.update_task_status(db_conn, task_id, "Archived")


def test_get_tasks_by_status(db_conn):
    t1 = db.create_task(db_conn, "Task A")
    db.create_task(db_conn, "Task B")

    db.update_task_status(db_conn, t1, "In Progress")

    in_progress_tasks = db.get_tasks_by_status(db_conn, "In Progress")
    assert len(in_progress_tasks) == 1
    assert in_progress_tasks[0][0] == t1


def test_get_all_tasks(db_conn):
    db.create_task(db_conn, "Task 1")
    db.create_task(db_conn, "Task 2")

    tasks = db.get_all_tasks(db_conn)
    assert len(tasks) == 2


def test_delete_task(db_conn):
    task_id = db.create_task(db_conn, "Temporary task")

    assert db.delete_task(db_conn, task_id) is True
    assert db.get_task_by_id(db_conn, task_id) is None


def test_delete_person_sets_task_person_id_to_null(db_conn):
    # Tests ON DELETE SET NULL foreign key constraint
    person_id = db.create_person(db_conn, "Hank")
    task_id = db.create_task(db_conn, "Hank's Task")
    db.assign_task(db_conn, task_id, person_id)

    # Delete person
    db.delete_person_by_id(db_conn, person_id)

    # Verify task still exists but person_id is set to None
    task = db.get_task_by_id(db_conn, task_id)
    assert task is not None
    assert task[5] is None
