import sqlalchemy
from sqlalchemy.orm import relationship

from .driver import Base


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    fullname = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    todo_items = relationship("ToDoItem", back_populates="owner")


class ToDoItem(Base):
    __tablename__ = "todoitems"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    subject = sqlalchemy.Column(sqlalchemy.String, index=True)
    body = sqlalchemy.Column(sqlalchemy.String, index=True)
    owner_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    owner = relationship("User", back_populates="todo_items")
