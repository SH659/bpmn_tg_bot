from uuid import UUID

from pydantic import BaseModel


class Bot(BaseModel):
    id: UUID
    name: str
    token: str | None
    diagram_id: UUID | None
    run_on_startup: bool = False
