from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from sqlmodel import select
from app.db.database import get_db
from app.models import User, UserCreate, TokenData
from app.core.dependency import oauth2_scheme
from dotenv import load_dotenv
import os
import jwt

# Carregar variáveis de ambiente
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY or not ALGORITHM or not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("One or more environment variables are not set")

# Instância do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função para verificar senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Função para gerar hash da senha
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Buscar usuário no banco de dados
def get_user(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

# Autenticar usuário
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# Criar token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Obter usuário autenticado pelo token
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if not user:
        raise credentials_exception
    return user

# Verificar se o usuário está ativo
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Criar novo usuário no banco
def create_user(db: Session, user: UserCreate) -> User:
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="User with this username already exists.")

    print("Criando novo usuário parte 2...")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        name=user.name,
        hashed_password=hashed_password,
        disabled=False
    )
    
    print("Adicionando novo usuário ao banco...")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print("Usuário criado com sucesso!")
    return new_user

# Verificar validade do token
def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return bool(payload.get("sub"))
    except InvalidTokenError:
        return False