"""
Database models for the Todo List application.

This module defines all SQLModel models used in the application:
- Category models (CategoryBase, Category, UpdateCategory, CategoryWithTodos)
- Todo models (TodoBase, Todo, UpdateTodo)
- User models (UserBase, User, UserCreate)
- Authentication models (Token, TokenData)

All models use UUID strings as primary keys and include proper relationships
between todos and categories.
"""

# Standard library imports
from datetime import date
from typing import Optional, List
from uuid import uuid4

# Third-party imports
from sqlmodel import SQLModel, Field, Relationship


class CategoryBase(SQLModel):
    """Base model for categories with common fields."""

    name: str
    created_at: date
    username: str


class Category(CategoryBase, table=True):
    """Database model for categories with relationships to todos."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    todos: List["Todo"] = Relationship(back_populates="category")


class DeleteTodosRequest(SQLModel):
    """Request model for bulk todo deletion."""

    ids: List[str]


class UpdateCategory(SQLModel):
    """Request model for category updates."""

    name: Optional[str] = None


class CategoryWithTodos(CategoryBase):
    """Response model for categories that includes their todos."""

    id: str
    todos: List["Todo"]


class TodoBase(SQLModel):
    """Base model for todos with common fields."""

    username: str
    content: str
    completed: bool = Field(default=False)
    created_at: date


class Todo(TodoBase, table=True):
    """Database model for todos with relationships to categories."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="todos")


class UpdateTodo(SQLModel):
    """Request model for todo updates."""

    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[str] = None


class UserBase(SQLModel):
    """Base model for users with common fields."""

    username: str
    name: str


class User(UserBase, table=True):
    """Database model for users."""

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    hashed_password: str
    disabled: Optional[bool] = Field(default=False)


class UserCreate(SQLModel):
    """Request model for user registration."""

    username: str
    name: str
    password: str


class Token(SQLModel):
    """Response model for authentication tokens."""

    access_token: str
    token_type: str


class TokenData(SQLModel):
    """Internal model for token payload data."""

    username: Optional[str] = None
