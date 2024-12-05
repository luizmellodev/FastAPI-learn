import datetime
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from app.schemas.todo import Todo

class Category(BaseModel):
    id: UUID = uuid4()
    name: str
    created_at: datetime.datetime

class UpdateCategory(BaseModel):
    name: Optional[str] = None

class CategoryWithTodos(Category):
    id: str
    name: str
    created_at: datetime.datetime
    todos: List[Todo]
