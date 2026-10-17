from itertools import count

from .schemas import User, UserCreate, UserUpdate


class EmailAlreadyExists(Exception):
    pass


class UserStorage:
    def __init__(self) -> None:
        self._users: list[User] = []
        self._ids = count(1)

    def clear(self) -> None:
        self._users.clear()
        self._ids = count(1)

    def list(self) -> list[User]:
        return list(self._users)

    def get(self, user_id: int) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def _check_email(self, email: str, exclude_id: int | None = None) -> None:
        if any(u.email == email and u.id != exclude_id for u in self._users):
            raise EmailAlreadyExists(email)

    def create(self, data: UserCreate) -> User:
        self._check_email(data.email)
        user = User(id=next(self._ids), **data.model_dump())
        self._users.append(user)
        return user

    def replace(self, user_id: int, data: UserCreate) -> User | None:
        return self.update(user_id, UserUpdate(**data.model_dump()))

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        user = self.get(user_id)
        if user is None:
            return None
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        if "email" in changes:
            self._check_email(changes["email"], exclude_id=user_id)
        updated = user.model_copy(update=changes)
        self._users[self._users.index(user)] = updated
        return updated

    def delete(self, user_id: int) -> bool:
        user = self.get(user_id)
        if user is None:
            return False
        self._users.remove(user)
        return True


storage = UserStorage()


def get_storage() -> UserStorage:
    return storage
