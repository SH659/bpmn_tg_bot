from uuid import UUID

from pydantic import BaseModel


class CreateBot(BaseModel):
    name: str = None
    token: str = None
    diagram_id: UUID = None


class UpdateBot(BaseModel):
    name: str = None
    token: str = None
    diagram_id: UUID = None
