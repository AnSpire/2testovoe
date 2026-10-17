from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from auth_api.config import ALGORITHM, SECRET_KEY
from auth_api.main import app
from auth_api.storage import storage

USER = {"username": "ivan", "email": "ivan@example.com", "password": "secret123"}


@pytest.fixture
def client():
    storage.clear()
    with TestClient(app) as c:
        yield c
    storage.clear()


def register(client, **overrides):
    return client.post("/auth/register", json=USER | overrides)


def login(client, username=USER["username"], password=USER["password"]):
    return client.post("/auth/login", json={"username": username, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def token(client):
    register(client)
    return login(client).json()["access_token"]


def test_register(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "ivan", "email": "ivan@example.com"}
    assert "password" not in response.text


def test_password_is_hashed(client):
    register(client)
    stored = storage.get_by_username("ivan")
    assert USER["password"] not in stored.password_hash


@pytest.mark.parametrize(
    "overrides",
    [{"password": "123"}, {"email": "bad"}, {"username": "a"}, {"username": "with space"}],
)
def test_register_validation(client, overrides):
    assert register(client, **overrides).status_code == 422


def test_register_duplicate(client):
    register(client)
    assert register(client).status_code == 409
    assert register(client, username="other").status_code == 409  # тот же email


def test_login_returns_token(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "ivan"


def test_login_wrong_password(client):
    register(client)
    assert login(client, password="wrong-pass").status_code == 401


def test_login_unknown_user(client):
    assert login(client, username="nobody").status_code == 401


def test_public_route_without_token(client):
    assert client.get("/public").status_code == 200


@pytest.mark.parametrize("path", ["/users/me", "/protected"])
def test_protected_requires_token(client, path):
    response = client.get(path)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_protected_with_token(client, token):
    me = client.get("/users/me", headers=auth_header(token))
    assert me.status_code == 200
    assert me.json()["username"] == "ivan"
    assert client.get("/protected", headers=auth_header(token)).status_code == 200


def test_invalid_token(client):
    assert client.get("/users/me", headers=auth_header("garbage")).status_code == 401


def test_token_with_wrong_signature(client, token):
    forged = jwt.encode({"sub": "ivan", "exp": datetime.now(UTC) + timedelta(minutes=5)},
                        "another-secret-key-at-least-32-bytes", algorithm=ALGORITHM)
    assert client.get("/users/me", headers=auth_header(forged)).status_code == 401


def test_expired_token(client):
    register(client)
    expired = jwt.encode({"sub": "ivan", "exp": datetime.now(UTC) - timedelta(minutes=1)},
                         SECRET_KEY, algorithm=ALGORITHM)
    response = client.get("/users/me", headers=auth_header(expired))
    assert response.status_code == 401
    assert response.json()["detail"] == "Срок действия токена истёк"


def test_token_for_deleted_user(client, token):
    storage.clear()
    assert client.get("/users/me", headers=auth_header(token)).status_code == 401
