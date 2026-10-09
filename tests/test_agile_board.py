from unittest.mock import MagicMock, patch

import pytest

from agile_board.agile_board import AgileBoard, InvalidInputError, NotFoundError


@pytest.fixture
def mock_db():
    with patch("agile_board.agile_board.db") as mocked:
        yield mocked


@pytest.fixture
def board():
    return AgileBoard(MagicMock())


def test_summary_groups_tasks_by_person(mock_db, board):
    mock_db.get_all_people.return_value = [(1, "Liam"), (2, "Priya")]
    mock_db.get_all_tasks.return_value = [
        (10, "Design schema", None, None, "Unassigned", 1),
        (11, "Set up CI", None, None, "In Progress", 1),
        (12, "Write docs", None, None, "Done", 2),
    ]

    summary = board.get_summary()

    assert summary == [
        {
            "personId": 1,
            "name": "Liam",
            "tasks": [
                {"taskId": 10, "title": "Design schema", "status": "backlog", "personId": 1},
                {"taskId": 11, "title": "Set up CI", "status": "inprogress", "personId": 1},
            ],
        },
        {
            "personId": 2,
            "name": "Priya",
            "tasks": [{"taskId": 12, "title": "Write docs", "status": "done", "personId": 2}],
        },
    ]


def test_summary_person_with_no_tasks(mock_db, board):
    mock_db.get_all_people.return_value = [(1, "Liam")]
    mock_db.get_all_tasks.return_value = []

    assert board.get_summary() == [{"personId": 1, "name": "Liam", "tasks": []}]


def test_summary_includes_unassigned_bucket(mock_db, board):
    mock_db.get_all_people.return_value = [(1, "Liam")]
    mock_db.get_all_tasks.return_value = [(10, "Orphan task", None, None, "Unassigned", None)]

    summary = board.get_summary()

    assert summary[-1] == {
        "personId": None,
        "name": None,
        "tasks": [{"taskId": 10, "title": "Orphan task", "status": "backlog", "personId": None}],
    }


def test_summary_empty(mock_db, board):
    mock_db.get_all_people.return_value = []
    mock_db.get_all_tasks.return_value = []

    assert board.get_summary() == []


def test_get_people(mock_db, board):
    mock_db.get_all_people.return_value = [(1, "Liam"), (2, "Priya")]

    assert board.get_people() == [{"personId": 1, "name": "Liam"}, {"personId": 2, "name": "Priya"}]


def test_create_person(mock_db, board):
    mock_db.get_person.return_value = None
    mock_db.create_person.return_value = 5

    assert board.create_person("  Jamell ") == {"personId": 5, "name": "Jamell"}
    mock_db.create_person.assert_called_once_with(board.conn, "Jamell")


@pytest.mark.parametrize("name", ["", "   ", None])
def test_create_person_blank_name(mock_db, board, name):
    with pytest.raises(InvalidInputError):
        board.create_person(name)
    mock_db.create_person.assert_not_called()


def test_create_person_duplicate(mock_db, board):
    mock_db.get_person.return_value = (1, "Liam")

    with pytest.raises(InvalidInputError):
        board.create_person("Liam")
    mock_db.create_person.assert_not_called()


def test_create_task(mock_db, board):
    mock_db.create_task.return_value = 7
    mock_db.get_task_by_id.return_value = (7, "New task", None, None, "Unassigned", None)

    assert board.create_task("New task") == {"taskId": 7, "title": "New task", "status": "backlog", "personId": None}


def test_create_task_blank_title(mock_db, board):
    with pytest.raises(InvalidInputError):
        board.create_task("  ")
    mock_db.create_task.assert_not_called()


def test_assign_task(mock_db, board):
    mock_db.get_person_by_id.return_value = (1, "Liam")
    mock_db.assign_task.return_value = True
    mock_db.get_task_by_id.return_value = (7, "New task", None, None, "Unassigned", 1)

    assert board.assign_task(7, 1)["personId"] == 1
    mock_db.assign_task.assert_called_once_with(board.conn, 7, 1)


def test_assign_task_unknown_person(mock_db, board):
    mock_db.get_person_by_id.return_value = None

    with pytest.raises(NotFoundError):
        board.assign_task(7, 99)
    mock_db.assign_task.assert_not_called()


def test_assign_task_unknown_task(mock_db, board):
    mock_db.get_person_by_id.return_value = (1, "Liam")
    mock_db.assign_task.return_value = False

    with pytest.raises(NotFoundError):
        board.assign_task(99, 1)


def test_get_engineer_tasks(mock_db, board):
    mock_db.get_person.return_value = (1, "Liam")
    mock_db.get_tasks_by_person.return_value = [(10, "Design schema", None, None, "In Progress", 1)]

    assert board.get_engineer_tasks("Liam") == [{"taskId": 10, "title": "Design schema", "status": "inprogress", "personId": 1}]
    mock_db.get_tasks_by_person.assert_called_once_with(board.conn, 1)


def test_get_engineer_tasks_unknown(mock_db, board):
    mock_db.get_person.return_value = None

    with pytest.raises(NotFoundError):
        board.get_engineer_tasks("Nobody")


@pytest.mark.parametrize("status, db_status", [("backlog", "Unassigned"), ("inprogress", "In Progress"), ("done", "Done")])
def test_move_task(mock_db, board, status, db_status):
    mock_db.update_task_status.return_value = True
    mock_db.get_task_by_id.return_value = (10, "Design schema", None, None, db_status, 1)

    assert board.move_task(10, status)["status"] == status
    mock_db.update_task_status.assert_called_once_with(board.conn, 10, db_status)


def test_move_task_invalid_status(mock_db, board):
    with pytest.raises(InvalidInputError):
        board.move_task(10, "archived")
    mock_db.update_task_status.assert_not_called()


def test_move_task_unknown_task(mock_db, board):
    mock_db.update_task_status.return_value = False

    with pytest.raises(NotFoundError):
        board.move_task(99, "done")
