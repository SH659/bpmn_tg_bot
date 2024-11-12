import uuid

from fastapi import APIRouter

from bpmn_be.bases.di import di
from schemas import CreateDiagram, UpdateDiagram, Diagram
from diagram.service import DiagramService

router = APIRouter()


@router.get("/", response_model=list[Diagram])
async def list_diagrams(
    ds: DiagramService = di(DiagramService)
):
    return await ds.get_all()


@router.get("/{diagram_id}", response_model=Diagram)
async def get_diagram(
    diagram_id: uuid.UUID,
    ds: DiagramService = di(DiagramService)
):
    return await ds.get_by_id(diagram_id)


@router.post("/", response_model=Diagram)
async def create_diagram(
    create_diagram_req: CreateDiagram,
    ds: DiagramService = di(DiagramService)
):
    return await ds.create(create_diagram_req)


@router.put("/{diagram_id}", response_model=Diagram)
async def update_diagram(
    diagram_id: uuid.UUID,
    diagram_update: UpdateDiagram,
    ds: DiagramService = di(DiagramService)
):
    return await ds.update(diagram_id, diagram_update)
