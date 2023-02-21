import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .auth.schemas import Token, TokenData
from .auth.utils import authenticate_user, create_access_token, hash_password
from .database import crud, models, schemas
from .database.driver import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
load_dotenv()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


@app.get("/")
def root():
    return {"message": "Take your baby steps towards productivity with Todoler"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
def get_current_user(current_user: models.User = Depends(get_current_active_user)):
    return current_user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user=user, hashed_password=hash_password(user.password))


@app.get("/users/me/items/", response_model=list[schemas.ToDoItem])
def get_all_todo_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    todo_items = crud.get_user_todo_items(
        db, current_user, skip=skip, limit=limit)
    return todo_items


@app.get("/users/me/items/{id}", response_model=schemas.ToDoItem)
def get_todo_item(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    todo_item = crud.get_user_todo_item(db, current_user, id)

    if todo_item is None:
        raise HTTPException(status_code=404, detail="ToDo item not found")

    return todo_item


@app.post("/users/me/items/", response_model=schemas.ToDoItem)
def create_todo_item_for_user(todo_item: schemas.ToDoItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.create_user_todo_item(db, current_user, todo_item=todo_item)


@app.put("/users/me/items/{id}", response_model=schemas.ToDoItem)
def update_todo_item(id: int, new_todo_item: schemas.ToDoItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.update_user_todo_item(db, current_user, id, new_todo_item)


@app.delete("/users/me/items/")
def delete_all_todo_items(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    crud.delete_user_todo_items(db, current_user)
    return {"message": "All todo items deleted successfully"}


@app.delete("/users/me/items/{id}")
def delete_todo_item(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    crud.delete_user_todo_item(db, current_user, id)
    return {"message": "Todo item deleted successfully"}
