import uuid
from typing import List

import httpx

from schemas import CreateDiagram, UpdateDiagram, Diagram


class DiagramApiClient:
    def __init__(self, base_url: str):
        self.base_url = f'{base_url}/diagrams'

    async def get_all(self) -> List[Diagram]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/")
            response.raise_for_status()
            return [Diagram(**item) for item in response.json()]

    async def get_by_id(self, diagram_id: uuid.UUID) -> Diagram:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{diagram_id}")
            response.raise_for_status()
            return Diagram(**response.json())

    async def get_by_name(self, name: str) -> Diagram:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/", params={"name": name})
            response.raise_for_status()
            diagrams = response.json()
            # Assuming only one diagram has the specified name; otherwise, handle appropriately.
            return Diagram(**diagrams[0]) if diagrams else None

    async def create(self, request: CreateDiagram) -> Diagram:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/", json=request.dict())
            response.raise_for_status()
            return Diagram(**response.json())

    async def update(self, diagram_id: uuid.UUID, request: UpdateDiagram) -> Diagram:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{self.base_url}/{diagram_id}", json=request.dict())
            response.raise_for_status()
            return Diagram(**response.json())
