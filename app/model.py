import datetime
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4

class Category(BaseModel):
    id: UUID = uuid4()
    name: str
    created_at: datetime.datetime

class UpdateCategory(BaseModel):
    name: Optional[str] = None

class Todo(BaseModel):
    id: UUID = uuid4()
    content: str
    completed: bool = False
    created_at: Optional[str]
    category_id: Optional[str]

class UpdateTodo(BaseModel):
    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[UUID] = None

class CategoryWithTodos(Category):
    id: str
    name: str
    created_at: datetime.datetime
    todos: List[Todo]