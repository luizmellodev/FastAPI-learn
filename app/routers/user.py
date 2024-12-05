from datetime import timedelta
from typing import Annotated
from app.schemas.user import User, Token, UserCreate
from app.core.dependency import oauth2_scheme, router
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, create_user, verify_token

@router.get("/users/me", response_model=User, tags=["users"])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
    
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        print("User not found")
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

@router.post("/user", response_model=User, tags=["users"], status_code=201)
async def create_new_user(user: UserCreate) -> UserCreate:
    new_user = create_user(user)
    return new_user

@router.get("/mytoken/")
async def read_items(token: str = Depends(oauth2_scheme)):
    verify = verify_token(token)
    if not verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": token}