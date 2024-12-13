from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from ..models import Users
from passlib.context import CryptContext
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

import os

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2Bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']


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
    firstname: str
    lastname: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Users).all()


@router.get("/user/{userId}", status_code=status.HTTP_200_OK)
async def getUserById(db: db_dependency, userId: int = Path(gt=0)):
    userModel = db.query(Users).filter(Users.id == userId).first()
    if userModel is not None:
        return userModel
    raise HTTPException(status_code=404, detail='User not found.')


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def createUser(db: db_dependency, createUserRequest: CreateUserRequest):
    createUserModel = Users(
        email=createUserRequest.email,
        username=createUserRequest.username,
        firstname=createUserRequest.firstname,
        lastname=createUserRequest.lastname,
        hashedPassword=bcryptContext.hash(createUserRequest.password),
        role=createUserRequest.role,
        is_active=True,
        phone_number=createUserRequest.phone_number
        
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
    userModel.firstname = userRequest.firstname
    userModel.lastname = userRequest.lastname
    userModel.role = userRequest.role
    userModel.hashedPassword = bcryptContext.hash(userRequest.password)

    db.add(userModel)
    db.commit()


@router.delete("/users/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteUser(db: db_dependency, userId: int = Path(gt=0)):
    userModel = db.query(Users).filter(Users.id == userId).first()
    if userModel is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Users).filter(Users.id == userId).delete()
    db.commit()


def authenticateUser(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(
        Users.username == username).first()
    if not user:
        return False
    if not bcryptContext.verify(password, user.hashedPassword):
        return False
    return user


def create_access_token(username: str, userId: int, role: str,  expiresDelta: timedelta):
    encode = {'sub': username, 'id': userId, 'role': role}
    expires = datetime.now(timezone.utc) + expiresDelta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2Bearer)]):

    if not token or token == "undefined":
        raise HTTPException(
            status_code=401, detail="Authorization token is missing")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')

        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not find the user")
        return {'userId': user_id, 'username': username, 'user_role': user_role}

    except JWTError as e:
        print("JWTError:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate userrrrr")


@router.post("/token", response_model=Token)
async def loginForAccessToken(formData: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticateUser(formData.username, formData.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user -- token")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
