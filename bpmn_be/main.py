import uuid

from fastapi import FastAPI, Depends, HTTPException
from injector import Injector, Module, Binder, singleton, InstanceProvider, ProviderOf
from starlette.middleware.cors import CORSMiddleware

from bpmn_be.bases.repo import Repo, InMemoryRepo
from bpmn_be.core.logs import configure_logging
from bpmn_be.diagram.errors import DiagramNotFoundError
from bpmn_be.diagram.models import Diagram
from bpmn_be.diagram.schemas import CreateDiagram, UpdateDiagram
from bpmn_be.diagram.service import DiagramService

configure_logging()


async def return_404(req, exc):
    raise HTTPException(status_code=404, detail="Not found")


app = FastAPI(
    exception_handlers={
        DiagramNotFoundError: return_404
    }
)
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(
            Repo[uuid.UUID, Diagram],
            to=InstanceProvider(InMemoryRepo()),
            scope=singleton
        )


injector = Injector([AppModule()])


def di(type):
    return Depends(injector.get(ProviderOf[type]).get)


@app.get("/diagrams/", response_model=list[Diagram])
async def list_diagrams(
    ds: DiagramService = di(DiagramService)
):
    return await ds.get_all()


@app.get("/diagrams/{diagram_id}", response_model=Diagram)
async def get_diagram(
    diagram_id: uuid.UUID,
    ds: DiagramService = di(DiagramService)
):
    return await ds.get_by_id(diagram_id)


@app.post("/diagrams/", response_model=Diagram)
async def create_diagram(
    create_diagram_req: CreateDiagram,
    ds: DiagramService = di(DiagramService)
):
    return await ds.create(create_diagram_req)


@app.put("/diagrams/{diagram_id}", response_model=Diagram)
async def update_diagram(
    diagram_id: uuid.UUID,
    diagram_update: UpdateDiagram,
    ds: DiagramService = di(DiagramService)
):
    return await ds.update(diagram_id, diagram_update)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=8000)
