# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import CORS_ORIGIN

from app.routers.todo import router as todo_router
from app.routers.categories import router as category_router
from app.routers.user import router as user_router
from app.db.database import create_db_and_tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(todo_router)
app.include_router(category_router)
app.include_router(user_router)


@app.on_event("startup")
def startup_event():
    create_db_and_tables()
