import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from auth_api.config import ALGORITHM, PRIVATE_KEY, PUBLIC_KEY
from auth_api.main import app
from auth_api.storage import sessions, storage

USER = {"username": "ivan", "email": "ivan@example.com", "password": "secret123"}


@pytest.fixture
def client():
    storage.clear()
    sessions.clear()
    with TestClient(app) as c:
        yield c
    storage.clear()
    sessions.clear()


def register(client, **overrides):
    return client.post("/auth/register", json=USER | overrides)


def login(client, username=USER["username"], password=USER["password"]):
    return client.post("/auth/login", json={"username": username, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def refresh(client, token):
    return client.post("/auth/refresh", json={"refresh_token": token})


def make_token(key=PRIVATE_KEY, exp_delta=timedelta(minutes=5), **claims):
    payload = {
        "sub": "ivan",
        "sid": "sid",
        "jti": "jti",
        "type": "access",
        "exp": datetime.now(UTC) + exp_delta,
    } | claims
    return jwt.encode(payload, key, algorithm=ALGORITHM)


@pytest.fixture
def tokens(client):
    register(client)
    return login(client).json()


@pytest.fixture
def token(tokens):
    return tokens["access_token"]


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
    assert register(client, username="other").status_code == 409


def test_login_returns_token(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    access = jwt.decode(body["access_token"], PUBLIC_KEY, algorithms=["RS256"])
    refresh_ = jwt.decode(body["refresh_token"], PUBLIC_KEY, algorithms=["RS256"])
    assert jwt.get_unverified_header(body["access_token"])["alg"] == "RS256"
    assert access["sub"] == refresh_["sub"] == "ivan"
    assert access["type"] == "access"
    assert refresh_["type"] == "refresh"
    assert access["sid"] == refresh_["sid"]


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
    sid = jwt.decode(token, options={"verify_signature": False})["sid"]
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    forged = make_token(key=other_key, sid=sid)
    assert client.get("/users/me", headers=auth_header(forged)).status_code == 401


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def test_hs256_signed_with_public_key_rejected(client, token):
    claims = jwt.decode(token, options={"verify_signature": False})
    pem = PUBLIC_KEY.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    signing_input = (
        _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        + "."
        + _b64(json.dumps(claims).encode())
    )
    signature = _b64(hmac.new(pem, signing_input.encode(), hashlib.sha256).digest())
    forged = f"{signing_input}.{signature}"
    assert client.get("/users/me", headers=auth_header(forged)).status_code == 401


def test_expired_token(client, token):
    sid = jwt.decode(token, options={"verify_signature": False})["sid"]
    expired = make_token(sid=sid, exp_delta=timedelta(minutes=-1))
    response = client.get("/users/me", headers=auth_header(expired))
    assert response.status_code == 401
    assert response.json()["detail"] == "Срок действия токена истёк"


def test_token_for_deleted_user(client, token):
    storage.clear()
    assert client.get("/users/me", headers=auth_header(token)).status_code == 401


def test_refresh_token_not_accepted_as_access(client, tokens):
    response = client.get("/users/me", headers=auth_header(tokens["refresh_token"]))
    assert response.status_code == 401


def test_access_token_not_accepted_as_refresh(client, tokens):
    assert refresh(client, tokens["access_token"]).status_code == 401


def test_refresh_rotates_tokens(client, tokens):
    response = refresh(client, tokens["refresh_token"])
    assert response.status_code == 200
    new = response.json()
    assert new["refresh_token"] != tokens["refresh_token"]
    assert new["access_token"] != tokens["access_token"]
    assert client.get("/users/me", headers=auth_header(new["access_token"])).status_code == 200
    assert refresh(client, new["refresh_token"]).status_code == 200


def test_refresh_token_reuse_revokes_session(client, tokens):
    new = refresh(client, tokens["refresh_token"]).json()

    reused = refresh(client, tokens["refresh_token"])
    assert reused.status_code == 401
    assert reused.json()["detail"] == "Refresh-токен уже использован, сессия отозвана"

    assert refresh(client, new["refresh_token"]).status_code == 401
    assert client.get("/users/me", headers=auth_header(new["access_token"])).status_code == 401


def test_logout_revokes_session(client, tokens):
    response = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 204

    me = client.get("/users/me", headers=auth_header(tokens["access_token"]))
    assert me.status_code == 401
    assert me.json()["detail"] == "Сессия отозвана"
    assert refresh(client, tokens["refresh_token"]).status_code == 401


def test_logout_keeps_other_sessions(client, tokens):
    other = login(client).json()
    client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert client.get("/users/me", headers=auth_header(other["access_token"])).status_code == 200
    assert refresh(client, other["refresh_token"]).status_code == 200


def test_expired_refresh_token(client, tokens):
    claims = jwt.decode(tokens["refresh_token"], options={"verify_signature": False})
    expired = make_token(
        sid=claims["sid"], jti=claims["jti"], type="refresh", exp_delta=timedelta(minutes=-1)
    )
    response = refresh(client, expired)
    assert response.status_code == 401
    assert response.json()["detail"] == "Срок действия токена истёк"


def test_refresh_for_deleted_user(client, tokens):
    storage.clear()
    assert refresh(client, tokens["refresh_token"]).status_code == 401
