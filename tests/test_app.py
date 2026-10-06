from unittest.mock import patch


def test_index_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_manager_page_returns_200(client):
    response = client.get("/manager")
    assert response.status_code == 200


def test_engineer_page_shows_name(client):
    response = client.get("/engineer/Liam")
    assert response.status_code == 200
    assert b"Liam's tasks" in response.data


def test_index_page_has_manager_button(client):
    response = client.get("/")
    assert b'href="/manager"' in response.data


def test_summary_json_uses_agile_board(client):
    fake_summary = [{"personId": 1, "name": "Liam", "tasks": []}]
    with patch("agile_board.app.AgileBoard") as mock_board:
        mock_board.return_value.get_summary.return_value = fake_summary
        response = client.get("/api/summary_json")

    assert response.status_code == 200
    assert response.get_json() == fake_summary
