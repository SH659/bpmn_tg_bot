from uuid import UUID

from pydantic import BaseModel


class CreateBot(BaseModel):
    name: str = None
    token: str = None
    diagram_id: UUID = None
    run_on_startup: bool = False


class UpdateBot(BaseModel):
    name: str = None
    token: str = None
    diagram_id: UUID = None
    run_on_startup: bool = None


class Bot(BaseModel):
    id: UUID
    name: str
    token: str | None
    diagram_id: UUID | None
    run_on_startup: bool = False
