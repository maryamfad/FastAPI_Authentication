from fastapi import APIRouter, Depends, Path

from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from fastapi.exceptions import HTTPException
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user


router = APIRouter(
    prefix='/todo',
    tags=['todo']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return db.query(Todos).filter(Todos.ownerId == user.get('id')).all()


@router.get("/{todoId}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency, db: db_dependency, todoId: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    todoModel = db.query(Todos).filter(Todos.id == todoId).filter(
        Todos.ownerId == user.get('id')).first()
    if todoModel is not None:
        return todoModel
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def creatTodo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    print("user", user)
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    todoModel = Todos(**todo_request.model_dump(), ownerId=user.get('id'))
    print(todoModel)
    db.add(todoModel)
    db.commit()


@router.put("/{todoId}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todoRequest: TodoRequest,
                      todoId: int = Path(gt=0),
                      ):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    todoModel = db.query(Todos).filter(Todos.id == todoId).filter(
        Todos.ownerId == user.get('id')).first()
    if todoModel is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    todoModel.title = todoRequest.title
    todoModel.description = todoRequest.description
    todoModel.priority = todoRequest.priority
    todoModel.complete = todoRequest.complete

    db.add(todoModel)
    db.commit()


@router.delete("/{todoId}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteTodo(user: user_dependency, db: db_dependency, todoId: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    todoModel = db.query(Todos).filter(Todos.id == todoId).filter(
        Todos.ownerId == user.get('id')).first()
    if todoModel is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todoId).filter(
        Todos.ownerId == user.get('id')).delete()
    db.commit()
