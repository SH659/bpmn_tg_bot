import uuid
from dataclasses import dataclass
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


class RunDiagramPayload(BaseModel):
    message: str
    state: dict


class RunDiagramResultDTO(BaseModel):
    actions: list[dict]
    new_state: dict


class RunDiagramResult(BaseModel):
    actions: list['Action']
    new_state: dict


@dataclass
class Action:
    pass


@dataclass
class SendMessage(Action):
    message: str


@dataclass
class WaitMessage(Action):
    pass
