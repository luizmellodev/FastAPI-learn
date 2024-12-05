import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.todo import Todo, UpdateTodo
from app.db.database_service import load_todos, save_todos, load_categories, save_categories
from uuid import UUID, uuid4
from app.core.security import get_current_active_user
from app.schemas.user import User

router = APIRouter()

@router.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}

@router.get("/todos", response_model=List[Todo], tags=["todos"])
async def get_todos(current_user: User = Depends(get_current_active_user)) -> List[Todo]:
    print(f"User {current_user.username} is authenticated.")
    todos_data = load_todos()
    
    return todos_data

@router.get("/todos/{id}", response_model=Todo, tags=["todos"])
async def get_todo_by_id(id: UUID, current_user: User = Depends(get_current_active_user)) -> Todo:
    print(f"User {current_user.username} is authenticated.")
    todos = load_todos()
    todo = next((todo for todo in todos if todo['id'] == str(id)), None)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    return todo

@router.post("/todos", response_model=Todo, tags=["todos"], status_code=201)
async def add_todo(todo: Todo, current_user: User = Depends(get_current_active_user)) -> Todo:
    print(f"User {current_user.username} is authenticated.")
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

    if todo.created_at:
        todo.created_at = datetime.datetime.now().isoformat()
    else:
        todo.created_at = datetime.datetime.now().isoformat()
    
    todo.username = current_user.username

    todos.append(todo.model_dump())
    save_todos(todos)
    
    return todo

@router.put("/todos/{id}", response_model=Todo, tags=["todos"])
async def update_todo(id: UUID, updated_todo: UpdateTodo, current_user: User = Depends(get_current_active_user)) -> Todo:
    print(f"User {current_user.username} is authenticated.")
    todos = load_todos()
    
    todo = next((todo for todo in todos if todo['id'] == str(id)), None)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    
    if updated_todo.content is not None:
        todo['content'] = updated_todo.content
    if updated_todo.completed is not None:
        todo['completed'] = updated_todo.completed
    if updated_todo.category_id is not None:
        todo['category_id'] = str(updated_todo.category_id)

    save_todos(todos)
    return todo

@router.delete("/todos/{id}", tags=["todos"], response_model=Todo)
async def delete_todo(id: UUID, current_user: User = Depends(get_current_active_user)) -> Todo:
    print(f"User {current_user.username} is authenticated.")
    todos = load_todos()
    todo_to_delete = next((todo for todo in todos if todo['id'] == str(id)), None)
    
    if not todo_to_delete:
        raise HTTPException(status_code=404, detail=f"Todo with id {id} not found.")
    
    new_todos = [todo for todo in todos if todo['id'] != str(id)]
    save_todos(new_todos)
    return todo_to_delete
