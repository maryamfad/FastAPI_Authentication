from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from starlette import status

router = APIRouter()

bcryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    email: str
    username: str
    firstName: str
    lastName: str
    password: str
    role: str


@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Users).all()


@router.get("/user/{userId}", status_code=status.HTTP_200_OK)
async def getUserById(db: db_dependency, userId: int = Path(gt=0)):
    userModel = db.query(Users).filter(Users.id == userId).first()
    if userModel is not None:
        return userModel
    raise HTTPException(status_code=404, detail='User not found.')


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def createUser(db: db_dependency, createUserRequest: CreateUserRequest):
    createUserModel = Users(
        email=createUserRequest.email,
        username=createUserRequest.username,
        firstName=createUserRequest.firstName,
        lastName=createUserRequest.lastName,
        hashedPassword=bcryptContext.hash(createUserRequest.password),
        role=createUserRequest.role,
        isActive=True
    )
    db.add(createUserModel)
    db.commit()


@router.put("/user/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def updateUser(db: db_dependency,
                     userRequest: CreateUserRequest,
                     userId: int = Path(gt=0),
                     ):
    userModel = db.query(Users).filter(Users.id == userId).first()
    if userModel is None:
        raise HTTPException(status_code=404, detail='User not found.')
    userModel.email = userRequest.email
    userModel.firstName = userRequest.firstName
    userModel.lastName = userRequest.lastName
    userModel.role = userRequest.role
    userModel.hashedPassword = userRequest.password

    db.add(userModel)
    db.commit()


@router.delete("/users/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteUser(db: db_dependency, userId: int = Path(gt=0)):
    userModel = db.query(Users).filter(Users.id == userId).first()
    if userModel is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Users).filter(Users.id == userId).delete()
    db.commit()
