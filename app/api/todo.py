from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID, uuid4

from app.core.database import get_async_session
from app.db.models import Todo as TodoModel
from app.db.models import Category as CategoryModel
from app.schemas.todo import Todo, UpdateTodo
from app.core.security import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}

@router.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> List[Todo]:
    print(f"User {current_user.username} is authenticated.")

    result = await session.execute(select(TodoModel).where(TodoModel.username == current_user.username))
    todos = result.scalars().all()

    return todos

@router.get("/todos/{id}", response_model=Todo, tags=["todos"])
async def get_todo_by_id(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> Todo:
    print(f"User {current_user.username} is authenticated.")

    todo = await session.get(TodoModel, id)
    
    if not todo or todo.username != current_user.username:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    
    return todo

@router.post("/todos", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(
    todo: Todo,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> Todo:
    print(f"User {current_user.username} is authenticated.")

    if not todo.id:
        todo.id = uuid4()

    # Verificar se a categoria existe
    category = None
    if todo.category_id:
        category = await session.get(CategoryModel, todo.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with id {todo.category_id} not found.")

    # Se não houver categoria, definir "Outros"
    if not category:
        category = await session.execute(select(CategoryModel).where(CategoryModel.name == "Outros"))
        category = category.scalars().first()
        if not category:
            raise HTTPException(status_code=500, detail="Default category 'Outros' not found.")

    new_todo = TodoModel(
        id=todo.id,
        content=todo.content,
        completed=todo.completed or False,
        created_at=datetime.now(),
        username=current_user.username,
        category_id=category.id
    )

    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)

    return new_todo

@router.put("/todos/{id}", response_model=Todo, tags=["todos"])
async def update_todo(
    id: UUID,
    updated_todo: UpdateTodo,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> Todo:
    print(f"User {current_user.username} is authenticated.")

    todo = await session.get(TodoModel, id)

    if not todo or todo.username != current_user.username:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")

    if updated_todo.content is not None:
        todo.content = updated_todo.content
    if updated_todo.completed is not None:
        todo.completed = updated_todo.completed
    if updated_todo.category_id is not None:
        category = await session.get(CategoryModel, updated_todo.category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with id {updated_todo.category_id} not found.")
        todo.category_id = updated_todo.category_id

    await session.commit()
    await session.refresh(todo)

    return todo

@router.delete("/todos/{id}", tags=["todos"], response_model=Todo)
async def delete_todo(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> Todo:
    print(f"User {current_user.username} is authenticated.")

    todo = await session.get(TodoModel, id)

    if not todo or todo.username != current_user.username:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")

    await session.delete(todo)
    await session.commit()

    return todo