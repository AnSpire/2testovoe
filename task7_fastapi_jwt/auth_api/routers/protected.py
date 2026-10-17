from fastapi import APIRouter

from ..dependencies import CurrentUser
from ..schemas import UserPublic

router = APIRouter(tags=["protected"])


@router.get("/public")
def public() -> dict[str, str]:
    return {"message": "Этот маршрут доступен без токена"}


@router.get("/users/me", response_model=UserPublic)
def read_me(user: CurrentUser) -> UserPublic:
    return UserPublic(id=user.id, username=user.username, email=user.email)


@router.get("/protected")
def protected(user: CurrentUser) -> dict[str, str]:
    return {"message": f"Привет, {user.username}! Это защищённый маршрут"}
