from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2Bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = '2add83603940657d0d2cf6a1aacc708e'
ALGORITHM = 'HS256'


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


class Token(BaseModel):
    accessToken: str
    tokenType: str


@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Users).all()


@router.get("/user/{userId}", status_code=status.HTTP_200_OK)
async def getUserById(db: db_dependency, userId: int = Path(gt=0)):
    userModel = db.query(Users).filter(Users.id == userId).first()
    if userModel is not None:
        return userModel
    raise HTTPException(status_code=404, detail='User not found.')


@router.post("/create_auth", status_code=status.HTTP_201_CREATED)
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


def authenticateUser(username: str, password: str, db):
    user = db_dependency.query(Users).filter(
        Users.username == username).first()
    if not user:
        return False
    if not bcryptContext.verify(password, user.hashedPassword):
        return False
    return user


def createAccessToken(username: str, userId: int, expiresDelta: timedelta):
    encode = {'sub': username, 'id': userId}
    expires = datetime.now(timezone.utc)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def getCurrentUser(token: Annotated[str, Depends(oauth2Bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        userId: int = payload.get('id')

        if userId is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {'userId': userId, 'username': username}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")


@router.post("/token", response_model=Token)
async def loginForAccessToken(formData: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticateUser(formData.username, formData.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = createAccessToken(user.username, user.id, timedelta(minutes=20))
    return {'accessToken': token, 'tokenType': 'bearer'}
