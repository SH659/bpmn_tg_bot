import uuid

from injector import inject

from bpmn_be.bases.repo import Repo
from bpmn_be.diagram.errors import DiagramNotFoundError
from bpmn_be.diagram.models import Diagram, empty_diagram_xml
from bpmn_be.diagram.schemas import CreateDiagram, UpdateDiagram


class DiagramService:
    @inject
    def __init__(self, diagram_repo: Repo[uuid.UUID, Diagram]):
        self.diagram_repo = diagram_repo

    async def get_all(self) -> list[Diagram]:
        return await self.diagram_repo.get_all()

    async def get_by_id(self, diagram_id: uuid.UUID) -> Diagram:
        diagram = await self.diagram_repo.get_by_id(diagram_id)
        if diagram is None:
            raise DiagramNotFoundError
        return diagram

    async def create(self, request: CreateDiagram) -> Diagram:
        diagram = Diagram(
            id=uuid.uuid4(),
            name=request.name,
            xml=request.xml or empty_diagram_xml,
        )
        await self.diagram_repo.create(diagram)
        return diagram

    async def update(self, diagram_id: uuid.UUID, request: UpdateDiagram) -> Diagram:
        old = await self.diagram_repo.get_by_id(diagram_id)
        new = Diagram(
            id=old.id,
            name=request.name or old.name,
            xml=request.xml or old.xml,
        )
        await self.diagram_repo.update(new)
        return new
