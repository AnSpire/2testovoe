"""Хранилище пользователей в памяти."""

from dataclasses import dataclass
from itertools import count


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
