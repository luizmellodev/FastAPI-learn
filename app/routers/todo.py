from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from app.models import Todo, UpdateTodo, User, Category, CategoryWithTodos
from app.db.database import get_db, SessionDep
from app.core.security import get_current_active_user
from sqlmodel import select
from datetime import datetime

router = APIRouter()

@router.get("/categories_with_todos", response_model=List[CategoryWithTodos], tags=["categories"])
async def get_categories_with_todos(session: SessionDep, current_user: User = Depends(get_current_active_user)) -> List[CategoryWithTodos]:
    categories = session.exec(select(Category)).all()
    
    for category in categories:
        category.todos = session.exec(select(Todo).where(Todo.category_id == category.id, Todo.username == current_user.username)).all()
    
    return categories

@router.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos(session: SessionDep, current_user: User = Depends(get_current_active_user)) -> List[Todo]:
    todos = session.exec(select(Todo).where(Todo.username == current_user.username)).all()
    return todos

@router.post("/todos", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(session: SessionDep, todo: Todo, current_user: User = Depends(get_current_active_user)) -> Todo:

    todo.username = current_user.username
    
    todo.id = str(UUID(todo.id)) if isinstance(todo.id, UUID) else str(todo.id)

    if isinstance(todo.created_at, str):
        try:
            todo.created_at = datetime.strptime(todo.created_at, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.put("/todos/{id}", response_model=Todo, tags=["todos"])
async def update_todo(session: SessionDep, id: str, updated_todo: UpdateTodo, current_user: User = Depends(get_current_active_user)) -> Todo:
    todo = session.get(Todo, id)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    if updated_todo.content:
        todo.content = updated_todo.content
    if updated_todo.completed is not None:
        todo.completed = updated_todo.completed
    if updated_todo.category_id:
        todo.category_id = updated_todo.category_id
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/todos/{id}", tags=["todos"], response_model=Todo)
async def delete_todo(session: SessionDep, id: str, current_user: User = Depends(get_current_active_user)) -> Todo:
    todo = session.get(Todo, id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    
    session.delete(todo)
    session.commit()
    return todo