"""
User router module.

This module handles all user-related operations including:
- User registration
- Authentication (login/logout)
- Token management
- User profile access

All operations follow OAuth2.0 password flow with JWT tokens for security.
"""

# Standard library imports
from datetime import timedelta
from typing import Annotated

# Third-party imports
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Local imports
from app.core.dependency import oauth2_scheme, router
from app.core.security import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    create_user,
    revoke_token,
    verify_token,
)
from app.db.database import get_db
from app.models import User, Token, UserCreate


@router.get("/users/me", response_model=User, tags=["users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get the current authenticated user's profile.

    Args:
        current_user: The authenticated user making the request

    Returns:
        User: The current user's profile
    """
    return current_user


@router.post("/token", response_model=Token, tags=["users"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db),
) -> Token:
    """
    Authenticate user and create access token.

    Args:
        form_data: The login form data (username and password)
        session: The database session

    Returns:
        Token: The JWT access token

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=User, tags=["users"], status_code=201)
async def create_new_user(user: UserCreate, session: Session = Depends(get_db)) -> User:
    """
    Register a new user.

    Args:
        user: The user data for registration
        session: The database session

    Returns:
        User: The created user

    Raises:
        HTTPException: If registration fails (e.g., username already exists)
    """
    try:
        new_user = create_user(db=session, user=user)
        return new_user
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to create user: {str(exc)}"
        ) from exc


@router.get("/verify-token", tags=["users"], status_code=200)
async def verify_token_endpoint(token: str = Depends(oauth2_scheme)) -> bool:
    """
    Verify if a JWT token is valid.

    Args:
        token: The JWT token to verify

    Returns:
        bool: True if token is valid, False otherwise
    """
    return verify_token(token)


@router.post("/logout", tags=["users"])
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Revoke a user's access token (logout).

    Args:
        token: The JWT token to revoke

    Returns:
        dict: A message confirming successful logout
    """
    revoke_token(token)
    return {"message": "Logout successful"}
