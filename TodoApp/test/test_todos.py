from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from sqlalchemy.pool import StaticPool
from ..main import app
from ..routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Todos

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False}, poolclass=StaticPool)


TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    return {'username': 'johndoe', 'id': 1, 'user_role': 'admin'}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    db = TestingSessionLocal()
    try:
        todo = Todos(
            title="Test Todo",
            description="This is a test todo",
            priority=5,
            complete=False,
            owner_id=1
        )
        db.add(todo)
        db.commit()
        db.refresh(todo)

        yield todo
    finally:
        with engine.connect() as connection:
            connection.execute(text('delete from todos'))
            connection.commit()
    db.close()


def test_read_all_authenticated(test_todo):
    response = client.get("/todo/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Test Todo', 'description': 'This is a test todo',
                                'complete': False, 'id': 1, 'priority': 5, 'owner_id': 1}]


def test_read_all_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Test Todo', 'description': 'This is a test todo',
                                'complete': False, 'id': 1, 'priority': 5, 'owner_id': 1}
    
def test_get_one_todo_authenticated_not_found(test_todo):
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}