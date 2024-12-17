
from ..main import app
from ..routers.todos import get_db, get_current_user
from fastapi import status
from ..models import Todos
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


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


def test_create_todo_authenticated(test_todo):
    request_data = {
        'title': 'New Todo',
        'description': 'New Todo description',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todo/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated Todo description',
        'priority': 4,
        'complete': True
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Updated Todo'
    assert model.description == 'Updated Todo description'


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated Todo description',
        'priority': 4,
        'complete': True
    }

    response = client.put('/todo/99', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}
