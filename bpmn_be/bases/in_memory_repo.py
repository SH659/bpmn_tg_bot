from typing import Optional

from bpmn_be.bases.repo import Repo, T_id, T_obj


class InMemoryRepo(Repo[T_id, T_obj]):
    def __init__(self, objects: list[T_obj] = None):
        self._storage = {}
        if objects:
            for obj in objects:
                self._storage[obj.id] = obj

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
