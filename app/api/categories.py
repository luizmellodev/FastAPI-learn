from datetime import datetime
from typing import List
from uuid import UUID
import uuid

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.db.models import Category, Todo
from app.schemas.category import Category as CategorySchema, UpdateCategory, CategoryWithTodos
from app.core.security import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.get("/categories", response_model=List[CategorySchema], tags=["categories"])
async def get_categories(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> List[CategorySchema]:
    print(f"User {current_user.username} is authenticated.")
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return categories

@router.get("/categories_with_todos", response_model=List[CategoryWithTodos], tags=["categories"])
async def get_categories_with_todos(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> List[CategoryWithTodos]:
    print(f"User {current_user.username} is authenticated.")
    
    categories_result = await db.execute(select(Category))
    todos_result = await db.execute(select(Todo).filter(Todo.username == current_user.username))
    
    categories = {category.id: CategoryWithTodos(**category.__dict__, todos=[]) for category in categories_result.scalars().all()}
    todos = todos_result.scalars().all()
    
    outros_category_id = get_outros_category_id(categories, db)
    
    for todo in todos:
        if todo.category_id in categories:
            categories[todo.category_id].todos.append(todo)
        else:
            if outros_category_id:
                categories[outros_category_id].todos.append(todo)
    
    return [category for category in categories.values() if category.todos]

@router.get("/categories/{id}", response_model=CategorySchema, tags=["categories"])
async def get_category_by_id(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> CategorySchema:
    print(f"User {current_user.username} is authenticated.")
    category = await db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    return category

@router.post("/categories", response_model=CategorySchema, tags=["categories"], status_code=201)
async def add_category(category: CategorySchema, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> CategorySchema:
    print(f"User {current_user.username} is authenticated.")
    new_category = Category(id=category.id, name=category.name, created_at=datetime.now())
    db.add(new_category)
    await db.commit()
    return new_category

@router.put("/categories/{id}", response_model=CategorySchema, tags=["categories"])
async def update_category(id: UUID, updated_category: UpdateCategory, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> CategorySchema:
    print(f"User {current_user.username} is authenticated.")
    category = await db.get(Category, id)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    
    if updated_category.name is not None:
        category.name = updated_category.name
    
    await db.commit()
    return category

@router.delete("/categories/{id}", tags=["categories"])
async def delete_category(id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> dict:
    print(f"User {current_user.username} is authenticated.")
    category = await db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    
    await db.delete(category)
    await db.commit()
    return {"message": f"Category with id {id} has been removed."}

# Função para verificar e adicionar a categoria "Outros" se necessário
async def get_outros_category_id(categories, db: AsyncSession):
    outros_category = next((cat for cat in categories.values() if cat.name == "Outros"), None)
    if not outros_category:
        new_id = str(uuid.uuid4())
        new_category = Category(id=new_id, name="Outros", created_at=datetime.now())
        db.add(new_category)
        await db.commit()
        return new_id
    return outros_category.id
