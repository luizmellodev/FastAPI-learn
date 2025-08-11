"""
Database models for the Todo List application.

This module defines SQLModel models that serve both as database tables and Pydantic models
for request/response validation. Models are organized by feature (Todo, Category, User)
with additional models for specific use cases like updates and authentication.
"""

from datetime import date
from typing import Optional, List
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    """Database and API model for categories."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    created_at: date
    username: str
    todos: List["Todo"] = Relationship(back_populates="category")


class UpdateCategory(SQLModel):
    """Request model for category updates with optional fields."""

    name: Optional[str] = None


class CategoryWithTodos(SQLModel):
    """Response model for categories that includes their todos."""

    id: str
    name: str
    created_at: date
    username: str
    todos: List["Todo"]


class Todo(SQLModel, table=True):
    """Database and API model for todos."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    username: str
    content: str
    completed: bool = Field(default=False)
    created_at: date
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="todos")


class UpdateTodo(SQLModel):
    """Request model for todo updates with optional fields."""

    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[str] = None


class User(SQLModel, table=True):
    """Database and API model for users."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    username: str
    name: str
    hashed_password: str
    disabled: Optional[bool] = Field(default=False)


class UserCreate(SQLModel):
    """Request model for user registration that includes plain text password."""

    username: str
    name: str
    password: str  # Plain text password that will be hashed


class Token(SQLModel):
    """Response model for authentication tokens."""

    access_token: str
    token_type: str


class TokenData(SQLModel):
    """Internal model for token payload data."""

    username: Optional[str] = None
