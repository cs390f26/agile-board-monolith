from unittest.mock import patch

from agile_board.agile_board import InvalidInputError, NotFoundError


def test_index_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_manager_page_returns_200(client):
    response = client.get("/manager")
    assert response.status_code == 200


def test_engineer_page_shows_name(client):
    with patch("agile_board.app.AgileBoard") as mock_board_cls:
        mock_board_cls.return_value.get_person.return_value = {"personId": 1, "name": "Liam"}
        response = client.get("/engineer/1")

    assert response.status_code == 200
    assert "Liam's tasks" in response.get_data(as_text=True)


def test_index_page_has_manager_button(client):
    response = client.get("/")
    assert b'href="manager"' in response.data


def test_summary_json_uses_agile_board(client):
    fake_summary = [{"personId": 1, "name": "Liam", "tasks": []}]
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.get_summary.return_value = fake_summary
        response = client.get("/api/summary_json")

    assert response.status_code == 200
    assert response.get_json() == fake_summary


def test_create_task_returns_201(client):
    fake_task = {"taskId": 1, "title": "New task", "status": "backlog", "personId": None}
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.create_task.return_value = fake_task
        response = client.post("/api/task/", json={"title": "New task"})

    assert response.status_code == 201
    assert response.get_json() == fake_task
    mock_board.return_value.create_task.assert_called_once_with("New task")


def test_create_task_invalid_returns_400(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.create_task.side_effect = InvalidInputError("title is required")
        response = client.post("/api/task/", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "title is required"}


def test_assign_task(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.assign_task.return_value = {"taskId": 3, "personId": 2}
        response = client.post("/api/task/3/assign", json={"person_id": "2"})

    assert response.status_code == 200
    mock_board.return_value.assign_task.assert_called_once_with(3, 2)


def test_assign_task_missing_person_returns_400(client):
    with patch("agile_board.app.AgileBoard"):
        response = client.post("/api/task/3/assign", json={})

    assert response.status_code == 400


def test_assign_task_not_found_returns_404(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.assign_task.side_effect = NotFoundError("task 3 not found")
        response = client.post("/api/task/3/assign", json={"person_id": 2})

    assert response.status_code == 404


def test_move_task_in_progress(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.move_task.return_value = {"taskId": 3, "status": "inprogress"}
        response = client.post("/api/task/3/1/inprogress")

    assert response.status_code == 200
    mock_board.return_value.move_task.assert_called_once_with(3, "inprogress")


def test_move_task_done(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.move_task.return_value = {"taskId": 3, "status": "done"}
        response = client.post("/api/task/3/1/done")

    assert response.status_code == 200
    mock_board.return_value.move_task.assert_called_once_with(3, "done")


def test_create_person_returns_201(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.create_person.return_value = {"personId": 4, "name": "Jamell"}
        response = client.post("/api/people", json={"name": "Jamell"})

    assert response.status_code == 201
    mock_board.return_value.create_person.assert_called_once_with("Jamell")


def test_create_person_missing_name_returns_400(client):
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.create_person.side_effect = InvalidInputError("name is required")
        response = client.post("/api/people", json={})

    assert response.status_code == 400
