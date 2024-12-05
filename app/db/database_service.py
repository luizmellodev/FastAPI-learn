import json
from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException

def load_data(filename: str, key: str) -> List[Dict[str, Any]]:
    try:
        with open(filename) as f:
            data = json.load(f)
            return data[key]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"{filename} not found.")
    except KeyError:
        raise HTTPException(status_code=500, detail=f"{key} not found in {filename}.")

def save_data(filename: str, key: str, data: List[Dict[str, Any]]) -> None:
    def convert_uuids(obj):
        if isinstance(obj, dict):
            return {k: convert_uuids(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_uuids(i) for i in obj]
        elif isinstance(obj, UUID):
            return str(obj)
        else:
            return obj

    data = convert_uuids(data)
    with open(filename, 'w') as f:
        json.dump({key: data}, f, indent=4)

def load_todos() -> List[Dict[str, Any]]:
    return load_data('todos.json', 'todos')

def save_todos(todos: List[Dict[str, Any]]) -> None:
    save_data('todos.json', 'todos', todos)

def load_categories() -> List[Dict[str, Any]]:
    return load_data('categories.json', 'categories')

def save_categories(categories: List[Dict[str, Any]]) -> None:
    save_data('categories.json', 'categories', categories)

def load_users() -> List[Dict[str, Any]]:
    return load_data('users.json', 'users')

def save_users(users: List[Dict[str, Any]]) -> None:
    save_data('users.json', 'users', users)
