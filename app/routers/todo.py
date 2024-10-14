import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.model import Todo, UpdateTodo
from app.db.database import load_todos, save_todos, load_categories, save_categories
from uuid import UUID, uuid4
import json

router = APIRouter()

@router.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}

@router.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos() -> List[Todo]:
    todos_data = load_todos()
    return todos_data

@router.get("/todos/{id}", response_model=Todo, tags=["todos"])
async def get_todo_by_id(id: UUID) -> Todo:
    todos = load_todos()
    todo = next((todo for todo in todos if todo['id'] == str(id)), None)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    return todo

@router.post("/todos", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(todo: Todo) -> Todo:
    todos = load_todos()
    
    if not todo.id:
        todo.id = str(uuid4())

    if any(existing_todo['id'] == todo.id for existing_todo in todos):
        raise HTTPException(status_code=400, detail="Todo with this ID already exists.")

    categories = load_categories()
    
    if todo.category_id:
        print(f"Category_id provided: {todo.category_id}")
        if not any(category['id'] == str(todo.category_id) for category in categories):
            print(f"Category with id {todo.category_id} not found.")
            raise HTTPException(status_code=404, detail=f"Category with id {todo.category_id} not found.")
        todo.category_id = str(todo.category_id) 
    else:
        print("No category_id provided. Setting to default category.")
        defaultCategory = next((category for category in categories if category['name'] == "Outros"), None)
        if not defaultCategory:
            raise HTTPException(status_code=500, detail="Error trying to find a 'default' category.")
        todo.category_id = defaultCategory['id']

    # Convert datetime to ISO 8601 string
    if todo.created_at:
        todo.created_at = datetime.datetime.now().isoformat()
    else:
        todo.created_at = datetime.datetime.now().isoformat()

    todos.append(todo.dict())
    save_todos(todos)
    
    return todo

@router.put("/todos/{id}", response_model=Todo, tags=["todos"])
async def update_todo(id: UUID, updated_todo: UpdateTodo) -> Todo:
    todos = load_todos()
    
    todo = next((todo for todo in todos if todo['id'] == str(id)), None)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    
    # Update the todo with provided fields
    if updated_todo.content is not None:
        todo['content'] = updated_todo.content
    if updated_todo.completed is not None:
        todo['completed'] = updated_todo.completed
    if updated_todo.category_id is not None:
        todo['category_id'] = str(updated_todo.category_id)

    save_todos(todos)
    return todo

@router.delete("/todos/{id}", tags=["todos"])
async def delete_todo(id: UUID) -> dict:
    todos = load_todos()
    new_todos = [todo for todo in todos if todo['id'] != str(id)]
    
    if len(new_todos) == len(todos):
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    
    save_todos(new_todos)
    return {"message": f"Todo with id {id} has been removed."}
