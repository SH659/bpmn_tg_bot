import atexit
import json
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from injector import Module, Binder, singleton, InstanceProvider
from starlette.middleware.cors import CORSMiddleware

from api.api_router import api_router
from bpmn_be.bases.di import injector
from bpmn_be.bases.logs import configure_logging
from bpmn_be.bases.pickle_repo import PickleRepo
from bpmn_be.bases.repo import Repo
from diagram.errors import BotNotFoundError
from diagram.errors import DiagramNotFoundError
from diagram.service import DiagramService
from schemas import Diagram
from settings import settings

configure_logging()


async def return_404(req, exc):
    raise HTTPException(status_code=404, detail="Not found")


@asynccontextmanager
async def lifespan(app: FastAPI):
    injector.binder.install(AppModule())
    diagram_repo: Repo[uuid.UUID, Diagram] = injector.get(Repo[uuid.UUID, Diagram])
    diagram_service: DiagramService = injector.get(DiagramService)

    for file in os.listdir('diagram_service/examples'):
        with open(f'diagram_service/examples/{file}') as f:
            diagram = Diagram(**json.load(f))
            try:
                await diagram_service.get_by_name(diagram.name)
            except DiagramNotFoundError:
                await diagram_repo.create(diagram)
    yield


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        diagram_repo = PickleRepo(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'diagram_repo.pkl'
            )
        )
        diagram_repo.load()
        atexit.register(diagram_repo.save)
        binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(diagram_repo), scope=singleton)


app = FastAPI(
    exception_handlers={
        DiagramNotFoundError: return_404,
        BotNotFoundError: return_404,
    },
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=settings.PORT)
