from fastapi import APIRouter, HTTPException, status

from ..dependencies import StorageDep
from ..schemas import Token, UserLogin, UserPublic, UserRegister
from ..security import create_access_token, hash_password, verify_password
from ..storage import UserAlreadyExists

router = APIRouter(prefix="/auth", tags=["auth"])


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
def login(data: UserLogin, storage: StorageDep) -> Token:
    user = storage.get_by_username(data.username)
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.username))
