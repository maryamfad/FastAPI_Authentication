from fastapi import FastAPI, Depends, Path
import models
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from fastapi.exceptions import HTTPException
from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def readt_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@app.put("/todo/{todoId}", status_code=status.HTTP_204_NO_CONTENT)
async def updateTodo(db: db_dependency,
                     todoRequest: TodoRequest,
                     todoId: int = Path(gt=0),
                     ):
    todoModel = db.query(Todos).filter(Todos.id == todoId).first()
    if todoModel is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    todoModel.title = todoRequest.title
    todoModel.description = todoRequest.description
    todoModel.priority = todoRequest.priority
    todoModel.complete = todoRequest.complete

    db.add(todoModel)
    db.commit()


@app.delete("/todo/{todoId}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteTodo(db: db_dependency, todoId: int = Path(gt=0)):
    todoModel = db.query(Todos).filter(Todos.id == todoId).first()
    if todoModel is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todoId).delete()
    db.commit()
