from typing import Optional

from pydantic import BaseModel


class ToDoItemBase(BaseModel):
    subject: str
    body: str | None = None


class ToDoItemCreate(ToDoItemBase):
    pass


class ToDoItemUpdate(ToDoItemBase):
    id: Optional[int]
    owner_id: Optional[int]
    subject: Optional[str]
    body: Optional[str]

    class Config:
        orm_mode = True


class ToDoItem(ToDoItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str
    fullname: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[ToDoItem] = []

    class Config:
        orm_mode = True
