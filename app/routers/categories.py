from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from datetime import datetime
from sqlmodel import select, Session
from app.models import Category, UpdateCategory, User, CategoryWithTodos
from app.db.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/categories", response_model=List[Category], tags=["categories"])
async def get_categories(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> List[Category]:
    categories = session.exec(select(Category).where(
        Category.username == current_user.username)).all()
    return categories


@router.post("/categories", response_model=CategoryWithTodos, tags=["categories"], status_code=201)
async def add_category(
    category: Category,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> CategoryWithTodos:
    category.username = current_user.username

    category.id = str(UUID(category.id)) if isinstance(
        category.id, UUID) else str(category.id)

    if isinstance(category.created_at, str):
        try:
            category.created_at = datetime.strptime(
                category.created_at, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    session.add(category)
    session.commit()
    session.refresh(category)

    return CategoryWithTodos(
        id=category.id,
        name=category.name,
        created_at=category.created_at,
        username=category.username,
        todos=[]
    )


@router.put("/categories/{id}", response_model=Category, tags=["categories"])
async def update_category(
    id: str,
    updated_category: UpdateCategory,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
) -> Category:
    category = session.get(Category, id)
    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with id {id} not found")

    if category.username != current_user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this category")

    if updated_category.name:
        category.name = updated_category.name

    session.commit()
    session.refresh(category)
    return category


@router.delete("/categories/{id}", tags=["categories"])
async def delete_category(
    id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db)
):
    category = session.get(Category, id)
    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with id {id} not found")

    if category.username != current_user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this category")

    session.delete(category)
    session.commit()
    return {"message": "Category deleted successfully"}
