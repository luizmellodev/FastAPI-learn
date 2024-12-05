from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4


class Todo(BaseModel):
    id: UUID = uuid4()
    username: str
    content: str
    completed: bool = False
    created_at: Optional[str]
    category_id: Optional[str]

class UpdateTodo(BaseModel):
    content: Optional[str] = None
    completed: Optional[bool] = None
    category_id: Optional[UUID] = None
