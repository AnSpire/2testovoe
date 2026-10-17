from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    """Частичное обновление: передаются только изменяемые поля."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None


class User(UserBase):
    id: int
