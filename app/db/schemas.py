from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    username: str
    name: str
    disabled: Optional[bool] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None