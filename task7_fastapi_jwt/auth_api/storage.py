from dataclasses import dataclass
from itertools import count
from threading import Lock

from .security import new_token_id


class UserAlreadyExists(Exception):
    pass


@dataclass
class StoredUser:
    id: int
    username: str
    email: str
    password_hash: str


class UserStorage:
    def __init__(self) -> None:
        self._users: list[StoredUser] = []
        self._ids = count(1)

    def clear(self) -> None:
        self._users.clear()
        self._ids = count(1)

    def get_by_username(self, username: str) -> StoredUser | None:
        return next((u for u in self._users if u.username == username), None)

    def create(self, username: str, email: str, password_hash: str) -> StoredUser:
        if any(u.username == username or u.email == email for u in self._users):
            raise UserAlreadyExists(username)
        user = StoredUser(next(self._ids), username, email, password_hash)
        self._users.append(user)
        return user


storage = UserStorage()


def get_storage() -> UserStorage:
    return storage


class SessionRevoked(Exception):
    pass


class RefreshTokenReused(Exception):
    pass


@dataclass
class Session:
    id: str
    username: str
    refresh_jti: str
    revoked: bool = False


class SessionStorage:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    def clear(self) -> None:
        self._sessions.clear()

    def create(self, username: str) -> Session:
        session = Session(new_token_id(), username, new_token_id())
        self._sessions[session.id] = session
        return session

    def is_active(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        return session is not None and not session.revoked

    def rotate(self, session_id: str, refresh_jti: str) -> str:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None or session.revoked:
                raise SessionRevoked(session_id)
            if session.refresh_jti != refresh_jti:
                session.revoked = True
                raise RefreshTokenReused(session_id)
            session.refresh_jti = new_token_id()
            return session.refresh_jti

    def revoke(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session is not None:
            session.revoked = True


sessions = SessionStorage()


def get_sessions() -> SessionStorage:
    return sessions
