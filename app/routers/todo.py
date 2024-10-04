from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.model import Todo, UpdateTodo
from app.db.database import load_todos, save_todos, load_categories
from uuid import UUID
import uuid

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
async def add_todo(todo: Todo, category_id: Optional[UUID] = None) -> Todo:
    todos = load_todos()
    
    if not todo.id:
        todo.id = str(uuid.uuid4())

    if any(existing_todo['id'] == todo.id for existing_todo in todos):
        raise HTTPException(status_code=400, detail="Todo with this ID already exists.")

    categories = load_categories()
    
    if category_id:
        if not any(category['id'] == str(category_id) for category in categories):
            raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found.")
        todo.category_id = str(category_id) 
    else:
        defaultCategory = next(category for category in categories if category['name'] == "Outros")
    if not any(defaultCategory):
        raise HTTPException(status_code=500, detail="Error trying to find a 'default' category.")
    
    todo.category_id = defaultCategory['id']

    todos.append(todo.model_dump())
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
        todo['category_id'] = updated_todo.category_id

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