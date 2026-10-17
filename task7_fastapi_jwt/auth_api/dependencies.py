from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .security import decode_access_token
from .storage import StoredUser, UserStorage, get_storage

bearer_scheme = HTTPBearer(auto_error=False)

StorageDep = Annotated[UserStorage, Depends(get_storage)]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    storage: StorageDep,
) -> StoredUser:
    if credentials is None:
        raise _unauthorized("Требуется токен")
    try:
        username = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Срок действия токена истёк")
    except jwt.InvalidTokenError:
        raise _unauthorized("Недействительный токен")

    user = storage.get_by_username(username)
    if user is None:
        raise _unauthorized("Пользователь не найден")
    return user


CurrentUser = Annotated[StoredUser, Depends(get_current_user)]
