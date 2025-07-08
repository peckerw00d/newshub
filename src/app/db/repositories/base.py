from typing import List, Optional, Type, TypeVar, Generic
from abc import ABC, abstractmethod

from sqlalchemy import Result, Select, Update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.base import Base


T = TypeVar("T")
ID = TypeVar("ID")

ModelType = TypeVar("ModelType", bound=Base)


class RepositoryInterface(ABC, Generic[T, ID]):
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        raise NotImplementedError

    async def get_all(self) -> List[T]:
        raise NotImplementedError

    async def create(self, obj: T) -> T:
        raise NotImplementedError

    async def delete(self, id: ID) -> None:
        raise NotImplementedError


class Repository(RepositoryInterface[T, ID]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: ID) -> Optional[T]:
        stmt = Select(self.model).where(self.model.id == id)
        result: Result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> List[T]:
        stmt = Select(self.model)
        result: Result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def update(self, id: int, data: dict) -> T:
        stmt = Update(self.model).where(self.model.id == id).values(**data).execution_options(synchronize_session="fetch")
        await self.session.execute(stmt)
        await self.session.commit()

        result = await self.session.execute(Select(self.model).where(self.model.id == id))
        return result.scalars().first()


    async def delete(self, id: ID) -> None:
        obj = await self.get_by_id(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
