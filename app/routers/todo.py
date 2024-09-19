from fastapi import APIRouter, HTTPException
from typing import List
from app.model import Todo
from app.db.database import load_todos, save_todos

router = APIRouter()
todos = load_todos()

@router.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}

@router.get("/todo", response_model=List[Todo], tags=["todos"])
async def get_todos() -> List[Todo]:
    return todos

@router.get("/todo/{id}", response_model=Todo, tags=["todos"])
async def get_todo_by_id(id: int) -> Todo:
    for todo in todos:
        if todo["id"] == id:
            return todo
    raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")

@router.post("/todo", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(todo: Todo) -> Todo:
    if any(existing_todo["id"] == todo.id for existing_todo in todos):
        raise HTTPException(status_code=400, detail="Todo with this ID already exists.")
    todos.append(todo.model_dump())
    save_todos(todos)
    return todo

@router.put("/todo/{id}", response_model=Todo, tags=["todos"])
async def update_todo(id: int, updated_todo: Todo) -> Todo:
    todo = next((todo for todo in todos if todo["id"] == id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    todo.update(updated_todo.model_dump()) 
    save_todos(todos)
    return updated_todo

@router.delete("/todo/{id}", tags=["todos"])
async def delete_todo(id: int) -> dict:
    todo = next((todo for todo in todos if todo["id"] == id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    todos.remove(todo)
    save_todos(todos)
    return {"message": f"Todo with id {id} has been removed."}
