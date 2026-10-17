import pytest
from fastapi.testclient import TestClient

from users_api.main import app
from users_api.storage import storage


@pytest.fixture
def client():
    storage.clear()
    with TestClient(app) as c:
        yield c
    storage.clear()


def create(client, name="Иван", email="ivan@example.com"):
    return client.post("/users", json={"name": name, "email": email})


def test_create_user(client):
    response = create(client)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Иван", "email": "ivan@example.com"}


def test_ids_increment(client):
    assert create(client, email="a@example.com").json()["id"] == 1
    assert create(client, email="b@example.com").json()["id"] == 2


def test_create_invalid_email(client):
    assert create(client, email="not-an-email").status_code == 422


def test_create_empty_name(client):
    assert create(client, name="").status_code == 422


def test_create_duplicate_email(client):
    create(client)
    assert create(client, name="Другой").status_code == 409


def test_list_users(client):
    assert client.get("/users").json() == []
    create(client, email="a@example.com")
    create(client, email="b@example.com")
    users = client.get("/users").json()
    assert [u["email"] for u in users] == ["a@example.com", "b@example.com"]


def test_get_user(client):
    create(client)
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Иван"


def test_get_missing_user(client):
    assert client.get("/users/42").status_code == 404


def test_replace_user(client):
    create(client)
    response = client.put("/users/1", json={"name": "Пётр", "email": "petr@example.com"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Пётр", "email": "petr@example.com"}


def test_replace_requires_all_fields(client):
    create(client)
    assert client.put("/users/1", json={"name": "Пётр"}).status_code == 422


def test_patch_user(client):
    create(client)
    response = client.patch("/users/1", json={"name": "Пётр"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Пётр", "email": "ivan@example.com"}


def test_patch_same_email_allowed(client):
    create(client)
    assert client.patch("/users/1", json={"email": "ivan@example.com"}).status_code == 200


def test_patch_to_taken_email(client):
    create(client, email="a@example.com")
    create(client, email="b@example.com")
    assert client.patch("/users/2", json={"email": "a@example.com"}).status_code == 409


def test_update_missing_user(client):
    assert client.patch("/users/42", json={"name": "X"}).status_code == 404
    assert client.put("/users/42", json={"name": "X", "email": "x@example.com"}).status_code == 404


def test_delete_user(client):
    create(client)
    assert client.delete("/users/1").status_code == 204
    assert client.get("/users/1").status_code == 404
    assert client.delete("/users/1").status_code == 404
