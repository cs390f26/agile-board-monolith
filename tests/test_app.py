def test_index_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_manager_page_returns_200(client):
    response = client.get("/manager")
    assert response.status_code == 200
