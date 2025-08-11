"""
Todo router module.

This module handles all todo-related operations including:
- Listing todos (with and without categories)
- Creating new todos
- Updating existing todos
- Deleting todos

All operations require user authentication and ensure that users can only
access and modify their own todos.
"""

# Standard library imports
from datetime import datetime
from typing import List
from uuid import UUID

# Third-party imports
from sqlmodel import Session, select
from fastapi import APIRouter, HTTPException, Depends, Query

# Local imports
from app.core.security import get_current_active_user
from app.db.database import get_db
from app.models import (
    Todo,
    UpdateTodo,
    User,
    Category,
    CategoryWithTodos,
)

router = APIRouter()


@router.get(
    "/categories_with_todos",
    response_model=List[CategoryWithTodos],
    tags=["categories"],
)
async def get_categories_with_todos(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[CategoryWithTodos]:
    """
    Retrieve all categories with their associated todos for the current user.

    Args:
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        List[CategoryWithTodos]: A list of categories, each containing its todos
    """
    categories = session.exec(
        select(Category).where(Category.username == current_user.username)
    ).all()

    result = []
    for category in categories:
        todos = session.exec(
            select(Todo).where(
                Todo.category_id == category.id, Todo.username == current_user.username
            )
        ).all()

        result.append(
            CategoryWithTodos(
                id=category.id,
                name=category.name,
                created_at=category.created_at,
                username=category.username,
                todos=todos,
            )
        )

    return result


@router.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[Todo]:
    """
    Retrieve all todos for the current user.

    Args:
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        List[Todo]: A list of all todos belonging to the current user
    """
    todos = session.exec(
        select(Todo).where(Todo.username == current_user.username)
    ).all()
    return todos


@router.post("/todos", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(
    todo: Todo,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Todo:
    """
    Create a new todo for the current user.

    Args:
        todo: The todo item to create
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        Todo: The created todo item

    Raises:
        HTTPException: If the date format is invalid
    """
    todo.username = current_user.username

    todo.id = str(UUID(todo.id)) if isinstance(todo.id, UUID) else str(todo.id)

    if isinstance(todo.created_at, str):
        try:
            todo.created_at = datetime.strptime(todo.created_at, "%Y-%m-%d").date()
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
            ) from exc

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.put("/todos/{todo_id}", response_model=Todo, tags=["todos"])
async def update_todo(
    todo_id: str,
    updated_todo: UpdateTodo,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Todo:
    """
    Update an existing todo.

    Args:
        todo_id: The ID of the todo to update
        updated_todo: The new todo data
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        Todo: The updated todo item

    Raises:
        HTTPException: If the todo is not found or user doesn't have permission
    """
    todo = session.get(Todo, todo_id)

    if not todo:
        raise HTTPException(
            status_code=404, detail=f"Todo with id {todo_id} not found."
        )

    if todo.username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail=f"You don't have permission to update todo with id {todo_id}",
        )
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
    session: Session = Depends(get_db),
) -> List[Todo]:
    """
    Delete multiple todos by their IDs.

    Args:
        ids: Comma-separated list of todo IDs to delete
        current_user: The authenticated user making the request
        session: The database session

    Returns:
        List[Todo]: The list of deleted todos

    Raises:
        HTTPException: If no valid IDs provided, todos not found, or user doesn't have permission
    """
    id_list = [todo_id.strip() for todo_id in ids.split(",") if todo_id.strip()]

    if not id_list:
        raise HTTPException(
            status_code=422,
            detail="No valid IDs provided. Please provide a comma-separated list of IDs.",
        )

    # pylint: disable=no-member
    todos_to_delete = session.exec(select(Todo).where(Todo.id.in_(id_list))).all()
    # pylint: enable=no-member

    if not todos_to_delete:
        raise HTTPException(
            status_code=404, detail=f"No Todos found for the provided IDs: {id_list}"
        )

    for todo in todos_to_delete:
        if todo.username != current_user.username:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to delete todo with id {todo.id}",
            )
        session.delete(todo)

    session.commit()
    return todos_to_delete
