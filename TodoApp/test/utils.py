from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest
from ..main import app
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
        print(f"Created Todo ID: {todo.id}")  # Debug output
        yield todo
    finally:
        with engine.connect() as connection:
            connection.execute(text('delete from todos'))
            connection.commit()
    db.close()
