import uuid

from fastapi import APIRouter

from bpmn_be.bases.di import di
from diagram.service import DiagramService
from schemas import CreateDiagram, UpdateDiagram, Diagram, RunDiagramResult

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


@router.post("/{diagram_id}/run")
async def step_diagram(
    diagram_id: uuid.UUID,
    message: str,
    state: dict,
    ds: DiagramService = di(DiagramService),
):
    actions, new_state = await ds.run_diagram(diagram_id, message=message, state=state)
    return RunDiagramResult(actions=actions, new_state=new_state)
