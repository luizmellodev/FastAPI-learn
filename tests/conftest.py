import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typing import Generator

from app.main import app
from app.db.database import get_db
from app.core.security import create_access_token
from app.models import User

# Cria um banco de dados em memória para testes


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

# Sobrescreve a dependência do banco de dados


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# Fixture para criar um usuário de teste


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        username="testuser",
        name="Test User",
        # senha: test123
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LcdYxEWhmKn1gMkgu",
        disabled=False
    )
    session.add(user)
    session.commit()
    return user

# Fixture para gerar um token de acesso


@pytest.fixture(name="test_token")
def test_token_fixture(test_user: User):
    return create_access_token(data={"sub": test_user.username})
