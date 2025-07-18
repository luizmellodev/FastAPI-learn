import pytest
import json
from httpx import AsyncClient
from datetime import date
from app.models import Todo, Category

# Teste para criar um TODO


@pytest.mark.asyncio
async def test_create_todo(client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    todo_data = {
        "username": "testuser",
        "content": "Test todo",
        "completed": False,
        "created_at": str(date.today())
    }

    response = client.post("/todos", headers=headers, json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == todo_data["content"]
    assert data["completed"] == todo_data["completed"]
    assert "id" in data

# Teste para listar TODOs


@pytest.mark.asyncio
async def test_list_todos(client, test_token, session):
    # Criar alguns TODOs de teste
    todo1 = Todo(
        username="testuser",
        content="Test todo 1",
        completed=False,
        created_at=date.today()
    )
    todo2 = Todo(
        username="testuser",
        content="Test todo 2",
        completed=True,
        created_at=date.today()
    )
    session.add(todo1)
    session.add(todo2)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(todo["content"] == "Test todo 1" for todo in data)
    assert any(todo["content"] == "Test todo 2" for todo in data)

# Teste para atualizar um TODO


@pytest.mark.asyncio
async def test_update_todo(client, test_token, session):
    # Criar um TODO para atualizar
    todo = Todo(
        username="testuser",
        content="Original todo",
        completed=False,
        created_at=date.today()
    )
    session.add(todo)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    update_data = {
        "content": "Updated todo",
        "completed": True
    }

    response = client.put(f"/todos/{todo.id}",
                          headers=headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == update_data["content"]
    assert data["completed"] == update_data["completed"]

# Teste para deletar TODOs


@pytest.mark.asyncio
async def test_delete_todos(client, test_token, session):
    # Criar TODOs para deletar
    todo1 = Todo(
        username="testuser",
        content="Todo to delete 1",
        completed=False,
        created_at=date.today()
    )
    todo2 = Todo(
        username="testuser",
        content="Todo to delete 2",
        completed=False,
        created_at=date.today()
    )
    session.add(todo1)
    session.add(todo2)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    params = {"ids": f"{todo1.id},{todo2.id}"}

    response = client.delete("/todos", headers=headers, params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Verificar se os TODOs foram realmente deletados
    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
