from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4

class Category(BaseModel):
    id: UUID = uuid4()
    name: str

class UpdateCategory(BaseModel):
    name: Optional[str] = None

class Todo(BaseModel):
    id: UUID = uuid4()
    content: str
    completed: bool = False
    category_id: Optional[UUID] = None

class UpdateTodo(BaseModel):
    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[UUID] = None

class CategoryWithTodos(Category):
    id: str
    name: str
    todos: List[Todo]