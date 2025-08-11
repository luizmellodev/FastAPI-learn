"""
Main application module.

This module initializes the FastAPI application with:
- Database setup and lifecycle management
- CORS middleware configuration
- Router registration for todos, categories, and users
"""

# Standard library imports
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from app.core.config import CORS_ORIGIN
from app.db.database import create_db_and_tables
from app.routers.categories import router as category_router
from app.routers.todo import router as todo_router
from app.routers.user import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Manage application lifecycle.

    Creates database tables on startup.

    Args:
        _: The FastAPI application instance (unused)
    """
    create_db_and_tables()
    yield  # Application runtime
    # Cleanup (if needed) would go here


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_router)
app.include_router(category_router)
app.include_router(user_router)
