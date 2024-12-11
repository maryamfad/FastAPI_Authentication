from fastapi import APIRouter, Depends, Path

from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos, Users
from fastapi.exceptions import HTTPException
from starlette import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from .auth import get_current_user


router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    print(user.get('id'))
    return db.query(Users).filter(Users.id == user.get('userId')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verificiation: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_model = db.query(Users).filter(Users.id == user.get('userId')).first()
    if not bcryptContext.verify(user_verificiation.password, user_model.hashedPassword):
        raise HTTPException(
            status_code=401, detail="Error on password verification")
    user_model.hashedPassword = bcryptContext.hash(
        user_verificiation.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user_model = db.query(Users).filter(Users.id == user.get('userId')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()