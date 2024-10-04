from fastapi import APIRouter, HTTPException
from typing import List
from app.model import Category, UpdateCategory, CategoryWithTodos, Todo
from app.db.database import load_categories, save_categories ,load_todos
from uuid import UUID
import uuid

router = APIRouter()

@router.get("/categories", response_model=List[Category], tags=["categories"])
async def get_categories() -> List[Category]:
    return load_categories()

@router.get("/categories_with_todos", response_model=List[CategoryWithTodos], tags=["categories"])
async def get_categories_with_todos() -> List[CategoryWithTodos]:
    categories = load_categories()
    todos = load_todos() 

    categories_dict = {category['id']: CategoryWithTodos(**category, todos=[]) for category in categories}

    outros_category_id = None
    if "Outros" not in [category['name'] for category in categories]:
        outros_category_id = str(uuid.uuid4())
        categories_dict[outros_category_id] = CategoryWithTodos(id=outros_category_id, name="Outros", todos=[])

    for todo in todos:
        category_id = todo.get('category_id')
        if category_id:
            if category_id in categories_dict:
                categories_dict[category_id].todos.append(Todo(**todo))
        else:
            if outros_category_id:
                categories_dict[outros_category_id].todos.append(Todo(**todo))

    return list(categories_dict.values())


@router.get("/categories/{id}", response_model=Category, tags=["categories"])
async def get_category_by_id(id: UUID) -> Category:
    categories = load_categories()
    category = next((category for category in categories if category['id'] == str(id)), None)
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    return category

@router.post("/categories", response_model=Category, tags=["categories"], status_code=201)
async def add_category(category: Category) -> Category:
    categories = load_categories()
    if any(existing_category['id'] == category.id for existing_category in categories):
        raise HTTPException(status_code=400, detail="Category with this ID already exists.")

    categories.append(category.model_dump())
    save_categories(categories)
    return category

@router.put("/categories/{id}", response_model=Category, tags=["categories"])
async def update_category(id: UUID, updated_category: UpdateCategory) -> Category:
    categories = load_categories()
    
    category = next((category for category in categories if category['id'] == str(id)), None)
    
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")
    
    if updated_category.name is not None:
        category['name'] = updated_category.name

    save_categories(categories)
    
    return category

@router.delete("/categories/{id}", tags=["categories"])
async def delete_category(id: UUID) -> dict:
    categories = load_categories()
    new_categories = [category for category in categories if category['id'] != str(id)]

    if len(new_categories) == len(categories):
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found.")

    save_categories(new_categories)
    return {"message": f"Category with id {id} has been removed."}
