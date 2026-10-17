from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..schemas import User, UserCreate, UserUpdate
from ..storage import EmailAlreadyExists, UserStorage, get_storage

router = APIRouter(prefix="/users", tags=["users"])

StorageDep = Annotated[UserStorage, Depends(get_storage)]


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")


def _email_taken() -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, detail="Email уже используется")


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, storage: StorageDep) -> User:
    try:
        return storage.create(data)
    except EmailAlreadyExists:
        raise _email_taken()


@router.get("", response_model=list[User])
def list_users(storage: StorageDep) -> list[User]:
    return storage.list()


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, storage: StorageDep) -> User:
    user = storage.get(user_id)
    if user is None:
        raise _not_found()
    return user


@router.put("/{user_id}", response_model=User)
def replace_user(user_id: int, data: UserCreate, storage: StorageDep) -> User:
    try:
        user = storage.replace(user_id, data)
    except EmailAlreadyExists:
        raise _email_taken()
    if user is None:
        raise _not_found()
    return user


@router.patch("/{user_id}", response_model=User)
def update_user(user_id: int, data: UserUpdate, storage: StorageDep) -> User:
    try:
        user = storage.update(user_id, data)
    except EmailAlreadyExists:
        raise _email_taken()
    if user is None:
        raise _not_found()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, storage: StorageDep) -> Response:
    if not storage.delete(user_id):
        raise _not_found()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
