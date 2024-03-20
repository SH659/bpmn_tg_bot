import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from injector import Module, Binder, singleton, InstanceProvider
from starlette.middleware.cors import CORSMiddleware

from api.api_router import api_router
from bases.pickle_repo import PickleRepo
from bases.repo import Repo
from core.di import injector
from core.logs import configure_logging
from diagram.errors import DiagramNotFoundError
from diagram.models import Diagram

configure_logging()


async def return_404(req, exc):
    raise HTTPException(status_code=404, detail="Not found")


@asynccontextmanager
async def lifespan(app: FastAPI):
    injector.binder.install(AppModule())
    yield


app = FastAPI(
    exception_handlers={
        DiagramNotFoundError: return_404
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


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        # binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(InMemoryRepo()), scope=singleton)
        diagram_repo = PickleRepo('diagram_repo.pkl')
        diagram_repo.load()
        print(len(diagram_repo._storage))
        binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(diagram_repo), scope=singleton)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=8000)
