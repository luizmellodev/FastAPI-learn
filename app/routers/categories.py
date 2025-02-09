from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from datetime import datetime
from sqlmodel import select
from app.models import Category, UpdateCategory, User, CategoryWithTodos
from app.db.database import get_db, SessionDep
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/categories", response_model=List[Category], tags=["categories"])
async def get_categories(session: SessionDep, current_user: User = Depends(get_current_active_user)) -> List[Category]:
    categories = session.exec(select(Category)).all()
    
    return categories

@router.post("/categories", response_model=CategoryWithTodos, tags=["categories"], status_code=201)
async def add_category(category: Category, session: SessionDep, current_user: User = Depends(get_current_active_user)) -> Category:
    category.id = str(UUID(category.id)) if isinstance(category.id, UUID) else str(category.id)

    if isinstance(category.created_at, str):
        try:
            category.created_at = datetime.strptime(category.created_at, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    session.add(category)
    session.commit()
    session.refresh(category)

    return CategoryWithTodos(
        id=category.id,
        name=category.name,
        created_at=category.created_at,
        todos=[]
    )

@router.put("/categories/{id}", response_model=Category, tags=["categories"])
async def update_category(id: str, updated_category: UpdateCategory, session: SessionDep, current_user: User = Depends(get_current_active_user)) -> Category:
    category = session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    if updated_category.name:
        category.name = updated_category.name
    session.commit()
    session.refresh(category)
    
    return category

@router.delete("/categories/{id}", tags=["categories"])
async def delete_category(id: str, session: SessionDep, current_user: User = Depends(get_current_active_user)):
    category = session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    session.delete(category)
    session.commit()
    return {"message": f"Category with id {id} has been removed."}