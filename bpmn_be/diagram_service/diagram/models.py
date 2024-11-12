import uuid
from typing import Optional

from pydantic import BaseModel


class Diagram(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    xml: str


with open('diagram_service/diagram/empty.bpmn', 'r') as file:
    empty_diagram_xml = file.read()
