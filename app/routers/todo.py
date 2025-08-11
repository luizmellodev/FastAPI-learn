from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from uuid import UUID
from app.models import DeleteTodosRequest, Todo, UpdateTodo, User, Category, CategoryWithTodos
from app.db.database import get_db
from sqlmodel import Session
from app.core.security import get_current_active_user
from sqlmodel import select
from datetime import datetime

router = APIRouter()


@router.get("/categories_with_todos", response_model=List[CategoryWithTodos], tags=["categories"])
async def get_categories_with_todos(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> List[CategoryWithTodos]:
    # Busca todas as categorias do usuário
    categories = session.exec(select(Category).where(
        Category.username == current_user.username)).all()

    # Para cada categoria, busca seus TODOs
    result = []
    for category in categories:
        todos = session.exec(select(Todo).where(
            Todo.category_id == category.id,
            Todo.username == current_user.username
        )).all()

        result.append(CategoryWithTodos(
            id=category.id,
            name=category.name,
            created_at=category.created_at,
            username=category.username,
            todos=todos
        ))

    return result


@router.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> List[Todo]:
    todos = session.exec(select(Todo).where(
        Todo.username == current_user.username)).all()
    return todos


@router.post("/todos", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(
    todo: Todo,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> Todo:
    todo.username = current_user.username

    todo.id = str(UUID(todo.id)) if isinstance(todo.id, UUID) else str(todo.id)

    if isinstance(todo.created_at, str):
        try:
            todo.created_at = datetime.strptime(
                todo.created_at, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.put("/todos/{id}", response_model=Todo, tags=["todos"])
async def update_todo(
    id: str,
    updated_todo: UpdateTodo,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> Todo:
    todo = session.get(Todo, id)

    if not todo:
        raise HTTPException(
            status_code=404, detail=f"Todo with id {id} not found.")
    if updated_todo.content:
        todo.content = updated_todo.content
    if updated_todo.completed is not None:
        todo.completed = updated_todo.completed
    if updated_todo.category_id:
        todo.category_id = updated_todo.category_id
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/todos", tags=["todos"], response_model=List[Todo])
async def delete_todos(
    ids: str = Query(..., description="Comma-separated list of todo IDs"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> List[Todo]:
    print(f"Received IDs string: {ids}")  # Debug print

    # Converte a string de IDs em uma lista
    id_list = [id.strip() for id in ids.split(",") if id.strip()]
    print(f"Parsed ID list: {id_list}")  # Debug print

    if not id_list:
        raise HTTPException(
            status_code=422,
            detail="No valid IDs provided. Please provide a comma-separated list of IDs."
        )

    todos_to_delete = session.exec(
        select(Todo).where(Todo.id.in_(id_list))).all()
    print(f"Found todos to delete: {len(todos_to_delete)}")  # Debug print

    if not todos_to_delete:
        raise HTTPException(
            status_code=404,
            detail=f"No Todos found for the provided IDs: {id_list}"
        )

    for todo in todos_to_delete:
        if todo.username != current_user.username:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to delete todo with id {todo.id}"
            )
        session.delete(todo)

    session.commit()
    return todos_to_delete
