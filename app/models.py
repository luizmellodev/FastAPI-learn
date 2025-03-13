from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4
from datetime import date

# Base Model para Categoria
class CategoryBase(SQLModel):
    name: str
    created_at: date
    
class Category(CategoryBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    todos: List["Todo"] = Relationship(back_populates="category")

# Model para requisição de exclusão de ToDos
class DeleteTodosRequest(SQLModel):
    ids: List[str]

# Update Model para Categoria
class UpdateCategory(SQLModel):
    name: Optional[str] = None

# Model com ToDos para retornar junto com a categoria
class CategoryWithTodos(CategoryBase):
    id: str
    todos: List["Todo"]

# Base Model para ToDo
class TodoBase(SQLModel):
    username: str
    content: str
    completed: bool = Field(default=False)
    created_at: date

class Todo(TodoBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="todos")

# Model de atualização para ToDo
class UpdateTodo(SQLModel):
    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[str] = None

# Model do Usuário
class UserBase(SQLModel):
    username: str
    name: str

class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    hashed_password: str
    disabled: Optional[bool] = Field(default=False)

# Create Model para Usuário
class UserCreate(SQLModel):
    username: str
    name: str
    password: str

# Token Model
class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Optional[str] = None
