"""
Categories router module.

This module handles all category-related operations including:
- Listing categories (with and without todos)
- Creating new categories
- Updating existing categories
- Deleting categories

All operations require user authentication and ensure that users can only
access and modify their own categories.
"""

# Standard library imports
from datetime import datetime
from typing import List
from uuid import UUID

# Third-party imports
from sqlmodel import select, Session
from fastapi import APIRouter, HTTPException, Depends

# Local imports
from app.core.security import get_current_active_user
from app.db.database import get_db
from app.models import Category, UpdateCategory, User, CategoryWithTodos

router = APIRouter()


@router.get("/categories", response_model=List[Category], tags=["categories"])
async def get_categories(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[Category]:
    """
    Retrieve all categories for the current user.

    Args:
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        List[Category]: A list of all categories belonging to the current user
    """
    categories = session.exec(
        select(Category).where(Category.username == current_user.username)
    ).all()
    return categories


@router.post(
    "/categories",
    response_model=CategoryWithTodos,
    tags=["categories"],
    status_code=201,
)
async def add_category(
    category: Category,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> CategoryWithTodos:
    """
    Create a new category for the current user.

    Args:
        category: The category to create
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        CategoryWithTodos: The created category with an empty todos list

    Raises:
        HTTPException: If the date format is invalid
    """
    category.username = current_user.username

    category.id = (
        str(UUID(category.id)) if isinstance(category.id, UUID) else str(category.id)
    )

    if isinstance(category.created_at, str):
        try:
            category.created_at = datetime.strptime(
                category.created_at, "%Y-%m-%d"
            ).date()
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
            ) from exc

    session.add(category)
    session.commit()
    session.refresh(category)

    return CategoryWithTodos(
        id=category.id,
        name=category.name,
        created_at=category.created_at,
        username=category.username,
        todos=[],
    )


@router.put("/categories/{category_id}", response_model=Category, tags=["categories"])
async def update_category(
    category_id: str,
    updated_category: UpdateCategory,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Category:
    """
    Update an existing category.

    Args:
        category_id: The ID of the category to update
        updated_category: The new category data
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        Category: The updated category

    Raises:
        HTTPException: If the category is not found or user doesn't have permission
    """
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with id {category_id} not found"
        )

    if category.username != current_user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this category"
        )

    if updated_category.name:
        category.name = updated_category.name

    session.commit()
    session.refresh(category)
    return category


@router.delete("/categories/{category_id}", tags=["categories"])
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> dict:
    """
    Delete a category.

    Args:
        category_id: The ID of the category to delete
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        dict: A message confirming the deletion

    Raises:
        HTTPException: If the category is not found or user doesn't have permission
    """
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=404, detail=f"Category with id {category_id} not found"
        )

    if category.username != current_user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this category"
        )

    session.delete(category)
    session.commit()
    return {"message": "Category deleted successfully"}
