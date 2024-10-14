import json
from typing import List
from uuid import UUID
from fastapi import HTTPException
from app.model import Todo, Category

def load_todos() -> List[Todo]:
    try:
        with open('todos.json') as f:
            data = json.load(f)
            return data['todos']
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="todos.json not found.")
    
def load_categories() -> List[Category]:
    try:
        with open('categories.json') as f:
            data = json.load(f)
            return data['categories']
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="categories.json not found.")

def save_todos(todos: List[dict]) -> None:
    def convert_uuids(obj):
        if isinstance(obj, dict):
            return {k: convert_uuids(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_uuids(i) for i in obj]
        elif isinstance(obj, UUID):
            return str(obj)
        else:
            return obj

    todos = convert_uuids(todos)
    with open('todos.json', 'w') as f:
        json.dump({"todos": todos}, f, indent=4)

def save_categories(categories: List[dict]) -> None:
    with open('categories.json', 'w') as f:
        json.dump({"categories": categories}, f, indent=4)
