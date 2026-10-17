from fastapi import APIRouter, HTTPException, status

from ..dependencies import SessionsDep, StorageDep, decode_or_401, unauthorized
from ..schemas import RefreshRequest, Token, UserLogin, UserPublic, UserRegister
from ..security import TokenType, create_token_pair, hash_password, verify_password
from ..storage import RefreshTokenReused, SessionRevoked, UserAlreadyExists

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue(username: str, session_id: str, refresh_jti: str) -> Token:
    access, refresh = create_token_pair(username, session_id, refresh_jti)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, storage: StorageDep) -> UserPublic:
    try:
        user = storage.create(data.username, data.email, hash_password(data.password))
    except UserAlreadyExists:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Пользователь с таким именем или email уже существует"
        )
    return UserPublic(id=user.id, username=user.username, email=user.email)


@router.post("/login", response_model=Token)
def login(data: UserLogin, storage: StorageDep, sessions: SessionsDep) -> Token:
    user = storage.get_by_username(data.username)
    if user is None or not verify_password(data.password, user.password_hash):
        raise unauthorized("Неверное имя пользователя или пароль")
    session = sessions.create(user.username)
    return _issue(user.username, session.id, session.refresh_jti)


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, storage: StorageDep, sessions: SessionsDep) -> Token:
    claims = decode_or_401(data.refresh_token, TokenType.REFRESH)
    try:
        new_jti = sessions.rotate(claims.sid, claims.jti)
    except SessionRevoked:
        raise unauthorized("Сессия отозвана")
    except RefreshTokenReused:
        raise unauthorized("Refresh-токен уже использован, сессия отозвана")
    if storage.get_by_username(claims.sub) is None:
        raise unauthorized("Пользователь не найден")
    return _issue(claims.sub, claims.sid, new_jti)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: RefreshRequest, sessions: SessionsDep) -> None:
    claims = decode_or_401(data.refresh_token, TokenType.REFRESH)
    sessions.revoke(claims.sid)
