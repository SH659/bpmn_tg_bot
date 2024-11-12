import uuid
from typing import Optional

from pydantic import BaseModel


class CreateDiagram(BaseModel):
    name: str = None
    xml: str = None


class UpdateDiagram(BaseModel):
    name: str = None
    xml: str = None


class Diagram(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    xml: str


class RunDiagramResult(BaseModel):
    actions: list[dict]
    new_state: dict
