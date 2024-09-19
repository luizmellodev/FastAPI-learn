from pydantic import BaseModel

class Todo(BaseModel):
    id: int
    item: str
    isDone: bool
    date: str
