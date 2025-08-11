from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4
from datetime import date


class CategoryBase(SQLModel):
    name: str
    created_at: date
    username: str


class Category(CategoryBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    todos: List["Todo"] = Relationship(back_populates="category")


class DeleteTodosRequest(SQLModel):
    ids: List[str]


class UpdateCategory(SQLModel):
    name: Optional[str] = None


class CategoryWithTodos(CategoryBase):
    id: str
    todos: List["Todo"]


class TodoBase(SQLModel):
    username: str
    content: str
    completed: bool = Field(default=False)
    created_at: date


class Todo(TodoBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="todos")


class UpdateTodo(SQLModel):
    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[str] = None


class UserBase(SQLModel):
    username: str
    name: str


class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    hashed_password: str
    disabled: Optional[bool] = Field(default=False)


class UserCreate(SQLModel):
    username: str
    name: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: Optional[str] = None
