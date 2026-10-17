from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .security import TokenClaims, TokenType, decode_token
from .storage import SessionStorage, StoredUser, UserStorage, get_sessions, get_storage

bearer_scheme = HTTPBearer(auto_error=False)

StorageDep = Annotated[UserStorage, Depends(get_storage)]
SessionsDep = Annotated[SessionStorage, Depends(get_sessions)]


def unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_or_401(token: str, token_type: TokenType) -> TokenClaims:
    try:
        return decode_token(token, token_type)
    except jwt.ExpiredSignatureError:
        raise unauthorized("Срок действия токена истёк")
    except jwt.InvalidTokenError:
        raise unauthorized("Недействительный токен")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    storage: StorageDep,
    sessions: SessionsDep,
) -> StoredUser:
    if credentials is None:
        raise unauthorized("Требуется токен")
    claims = decode_or_401(credentials.credentials, TokenType.ACCESS)
    if not sessions.is_active(claims.sid):
        raise unauthorized("Сессия отозвана")

    user = storage.get_by_username(claims.sub)
    if user is None:
        raise unauthorized("Пользователь не найден")
    return user


CurrentUser = Annotated[StoredUser, Depends(get_current_user)]
