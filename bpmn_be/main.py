import logging
import sys
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
diagrams = {}

with open('empty.bpmn', 'r') as file:
    empty_diagram = file.read()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)-9s %(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Diagram(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    xml: str


class CreateDiagram(BaseModel):
    name: str = None
    xml: str = None


class UpdateDiagram(BaseModel):
    name: str = None
    xml: str = None


@app.get("/diagrams/", response_model=List[Diagram])
async def list_diagrams():
    return list(diagrams.values())


@app.get("/diagrams/{diagram_id}", response_model=Diagram)
async def get_diagram(diagram_id: uuid.UUID):
    if diagram_id in diagrams:
        logger.info(f"Returning diagram {diagram_id}. XML len={len(diagrams[diagram_id].xml)}")
        return diagrams[diagram_id]
    raise HTTPException(status_code=404, detail="Diagram not found")


@app.post("/diagrams/", response_model=Diagram)
async def create_empty_diagram(create_diagram_req: CreateDiagram):
    diagram = Diagram(
        id=uuid.uuid4(),
        name=create_diagram_req.name,
        xml=create_diagram_req.xml or empty_diagram,
    )
    diagrams[diagram.id] = diagram
    logger.info(f"Created diagram {diagram.id}")
    return diagram


@app.put("/diagrams/{diagram_id}", response_model=Diagram)
async def update_diagram(diagram_id: uuid.UUID, diagram_update: UpdateDiagram):
    if diagram_id in diagrams:
        old_diagram = diagrams[diagram_id]
        new_diagram = Diagram(
            id=old_diagram.id,
            name=diagram_update.name or old_diagram.name,
            xml=diagram_update.xml or old_diagram.xml,
        )
        diagrams[diagram_id] = new_diagram
        return new_diagram
    logger.info("Diagram not found")
    raise HTTPException(status_code=404, detail="Diagram not found")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=8000)
