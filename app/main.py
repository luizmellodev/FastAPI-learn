from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.todo import router as todo_router
from app.routers.categories import router as category_router
from app.core.config import CORS_ORIGIN

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