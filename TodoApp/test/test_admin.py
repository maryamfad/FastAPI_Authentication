from ..main import app
from ..routers.admin import get_db, get_current_user
from fastapi import status
from ..models import Todos
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


def test_admin_get_all_todos(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Test Todo', 'description': 'This is a test todo',
                                'complete': False, 'id': 1, 'priority': 5, 'owner_id': 1}]


def test_admin_delete_todo(test_todo):
    db = next(override_get_db())  # Use the same session as the endpoint
    try:
        # Confirm the todo exists before deletion
        model = db.query(Todos).filter(Todos.id == test_todo.id).first()
        assert model is not None

        # Perform the DELETE request
        response = client.delete(f"/admin/todo/{test_todo.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Confirm the todo is deleted
        model = db.query(Todos).filter(Todos.id == test_todo.id).first()
        assert model is None
    finally:
        db.close()
