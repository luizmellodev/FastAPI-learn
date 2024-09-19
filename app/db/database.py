import json
from typing import List
from fastapi import HTTPException

def load_todos() -> List[dict]:
    try:
        with open("db.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading todos data.")

def save_todos(todos: List[dict]) -> None:
    with open("db.json", "w") as file:
        json.dump(todos, file, indent=4)
