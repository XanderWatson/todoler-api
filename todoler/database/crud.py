from sqlalchemy.orm import Session

from .models import ToDoItem, User
from .schemas import ToDoItemCreate, ToDoItemUpdate, UserCreate


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(username=user.username, email=user.email,
                   fullname=user.fullname, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_todo_items(db: Session, user: User, skip: int = 0, limit: int = 10):
    return db.query(ToDoItem).filter(ToDoItem.owner_id == user.id).offset(skip).limit(limit).all()


def get_user_todo_item(db: Session, user: User, item_id: int):
    return db.query(ToDoItem).filter(ToDoItem.owner_id == user.id, ToDoItem.id == item_id).first()


def create_user_todo_item(db: Session, user: User, todo_item: ToDoItemCreate):
    db_todo_item = ToDoItem(**todo_item.dict(), owner_id=user.id)
    db.add(db_todo_item)
    db.commit()
    db.refresh(db_todo_item)
    return db_todo_item


def update_user_todo_item(db: Session, user: User, todo_item_id: int, new_todo_item: ToDoItemUpdate):
    db_todo_item = db.query(ToDoItem).filter(
        ToDoItem.owner_id == user.id, ToDoItem.id == todo_item_id).one_or_none()
    if db_todo_item is None:
        return None

    for var, value in vars(new_todo_item).items():
        setattr(db_todo_item, var, value)

    db.add(db_todo_item)
    db.commit()
    db.refresh(db_todo_item)

    return db_todo_item


def delete_user_todo_item(db: Session, user: User, todo_item_id: int):
    db_todo_item = db.query(ToDoItem).filter(
        ToDoItem.owner_id == user.id, ToDoItem.id == todo_item_id)
    db_todo_item.delete()
    db.commit()


def delete_user_todo_items(db: Session, user: User):
    db_todo_items = db.query(ToDoItem).filter(ToDoItem.owner_id == user.id)
    db_todo_items.delete()
    db.commit()
