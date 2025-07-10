from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.app.db.repositories.base import Repository


@pytest_asyncio.fixture(scope="function")
async def mock_async_session():
    session = AsyncMock(spec=AsyncSession)

    session.execute = AsyncMock(
        return_value=MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(first=MagicMock(return_value=None))
            )
        )
    )

    session.add = MagicMock()
    session.commit = AsyncMock()

    return session


@pytest_asyncio.fixture(scope="function")
async def test_model():
    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "users"

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
        password: Mapped[str] = mapped_column(String)
        email: Mapped[str] = mapped_column(String, unique=True)

    return User


@pytest_asyncio.fixture(scope="function")
async def base_repo(mock_async_session, test_model):
    return Repository(session=mock_async_session, model=test_model)


@pytest_asyncio.fixture(scope="function")
async def test_user(test_model):
    User = test_model
    return User(
        id=1, username="User202", email="example@example.com", password="qwerty"
    )
