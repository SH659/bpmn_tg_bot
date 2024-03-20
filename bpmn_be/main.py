import uuid

from fastapi import FastAPI, HTTPException
from injector import Module, Binder, singleton, InstanceProvider
from starlette.middleware.cors import CORSMiddleware

from bpmn_be.api.api_router import api_router
from bpmn_be.bases.repo import Repo, InMemoryRepo
from bpmn_be.core.di import injector
from bpmn_be.core.logs import configure_logging
from bpmn_be.diagram.errors import DiagramNotFoundError
from bpmn_be.diagram.models import Diagram

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
app.include_router(api_router)


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(InMemoryRepo()), scope=singleton)


injector.binder.install(AppModule())

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=8000)
