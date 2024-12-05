from typing import Annotated, Any, Dict
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from app.schemas.user import User, UserCreate, TokenData, UserInDB
from app.db.database_service import load_users, save_users
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.core.dependency import oauth2_scheme
from dotenv import load_dotenv
import os
import jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY or not ALGORITHM or not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("One or more environment variables are not set")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

user_db = load_users()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    if username in user_db:
        user_dict = user_db[username]
        return UserInDB(**user_dict)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_user(user: UserCreate) -> Dict[str, Any]:
    users = load_users()

    if user.username in users:
        raise HTTPException(status_code=400, detail="User with this username already exists.")

    hashed_password = get_password_hash(user.password)
    
    new_user = UserInDB(
        username=user.username,
        name=user.name,
        hashed_password=hashed_password,
        disabled=user.disabled
        
    )

    users[user.username] = new_user.model_dump()
    save_users(users)

    return_user = User(**users[user.username])
    return return_user

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return False
        return True
    except InvalidTokenError:
        return False
    