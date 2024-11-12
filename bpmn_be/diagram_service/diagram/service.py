import dataclasses
import uuid

from injector import inject

from bpmn_be.bases.repo import Repo
from diagram.errors import DiagramNotFoundError
from diagram.executor.bpmn_executor import BpmnExecutor, Data, State
from diagram.models import empty_diagram_xml
from diagram.parser.bpmn_parser import xml_to_process
from schemas import CreateDiagram, UpdateDiagram, Diagram


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

    async def get_by_name(self, name: str) -> Diagram:
        diagrams = await self.diagram_repo.get_all()
        for diagram in diagrams:
            if diagram.name == name:
                return diagram
        raise DiagramNotFoundError

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
        if old is None:
            raise DiagramNotFoundError
        new = Diagram(
            id=old.id,
            name=request.name or old.name,
            xml=request.xml or old.xml,
        )
        await self.diagram_repo.update(new)
        return new

    async def run_diagram(self, diagram_id: uuid.UUID, message: str, state: dict):
        diagram = await self.get_by_id(diagram_id)
        process = xml_to_process(diagram.xml)
        executor = BpmnExecutor(process)
        actions, new_state = await executor.step(Data(message), State(**state))
        actions = [dataclasses.asdict(action) for action in actions]
        return actions, new_state
