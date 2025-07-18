import pytest
from datetime import date
from app.models import Category, Todo


@pytest.mark.asyncio
async def test_create_category(client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    category_data = {
        "name": "Test Category",
        "created_at": str(date.today()),
        "username": "testuser"
    }

    response = client.post("/categories", headers=headers, json=category_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]
    assert "id" in data
    assert data["todos"] == []


@pytest.mark.asyncio
async def test_list_categories_with_todos(client, test_token, session):
    # Criar uma categoria
    category = Category(
        name="Test Category",
        created_at=date.today(),
        username="testuser"
    )
    session.add(category)
    session.commit()

    # Criar um TODO nessa categoria
    todo = Todo(
        username="testuser",
        content="Test todo",
        completed=False,
        created_at=date.today(),
        category_id=category.id
    )
    session.add(todo)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/categories_with_todos", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Category"
    assert len(data[0]["todos"]) == 1
    assert data[0]["todos"][0]["content"] == "Test todo"


@pytest.mark.asyncio
async def test_list_empty_category(client, test_token, session):
    # Criar uma categoria sem TODOs
    category = Category(
        name="Empty Category",
        created_at=date.today(),
        username="testuser"
    )
    session.add(category)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/categories_with_todos", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Empty Category"
    assert data[0]["todos"] == []


@pytest.mark.asyncio
async def test_update_category(client, test_token, session):
    # Criar uma categoria para atualizar
    category = Category(
        name="Old Name",
        created_at=date.today(),
        username="testuser"
    )
    session.add(category)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    update_data = {
        "name": "New Name"
    }

    response = client.put(
        f"/categories/{category.id}", headers=headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_category(client, test_token, session):
    # Criar uma categoria para deletar
    category = Category(
        name="To Delete",
        created_at=date.today(),
        username="testuser"
    )
    session.add(category)
    session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.delete(f"/categories/{category.id}", headers=headers)
    assert response.status_code == 200

    # Verificar se a categoria foi realmente deletada
    response = client.get("/categories_with_todos", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
