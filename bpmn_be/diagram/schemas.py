import uuid

from pydantic import BaseModel


class CreateDiagram(BaseModel):
    name: str = None
    xml: str = None


class UpdateDiagram(BaseModel):
    name: str = None
    xml: str = None
