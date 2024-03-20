from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T_id = TypeVar("T_id")
T_obj = TypeVar("T_obj")


class Repo(Generic[T_id, T_obj], ABC):
    @abstractmethod
    async def get_by_id(self, id: T_id) -> Optional[T_obj]:
        pass

    @abstractmethod
    async def create(self, obj: T_obj) -> T_obj:
        pass

    @abstractmethod
    async def update(self, obj: T_obj) -> T_obj:
        pass

    @abstractmethod
    async def delete(self, id: T_id) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[T_obj]:
        pass

    @abstractmethod
    async def exists(self, id: T_id) -> bool:
        pass


class InMemoryRepo(Repo[T_id, T_obj]):
    def __init__(self):
        self._storage = {}

    async def get_by_id(self, id: T_id) -> Optional[T_obj]:
        return self._storage.get(id)

    async def create(self, obj: T_obj) -> T_obj:
        self._storage[obj.id] = obj
        return obj

    async def update(self, obj: T_obj) -> T_obj:
        self._storage[obj.id] = obj
        return obj

    async def delete(self, id: T_id) -> None:
        del self._storage[id]

    async def get_all(self) -> list[T_obj]:
        return list(self._storage.values())

    async def exists(self, id: T_id) -> bool:
        return id in self._storage
