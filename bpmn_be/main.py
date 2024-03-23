import atexit
import json
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from injector import Module, Binder, singleton, InstanceProvider
from starlette.middleware.cors import CORSMiddleware

from api.api_router import api_router
from bases.in_memory_repo import InMemoryRepo
from bases.pickle_repo import PickleRepo
from bases.repo import Repo
from core.di import injector
from core.logs import configure_logging
from core.settings import settings
from diagram.errors import DiagramNotFoundError
from diagram.models import Diagram
from tg_bot.models import Bot
from tg_bot.service import TgBotService

configure_logging()


async def return_404(req, exc):
    raise HTTPException(status_code=404, detail="Not found")


@asynccontextmanager
async def lifespan(app: FastAPI):
    injector.binder.install(AppModule())
    diagram_repo: Repo[uuid.UUID, Diagram] = injector.get(Repo[uuid.UUID, Diagram])
    # with open('examples/echo_diagram.json') as f:
    with open('examples/curl_example.json') as f:
        diagram = Diagram(**json.load(f))
        await diagram_repo.create(diagram)

    bot_repo: Repo[uuid.UUID, Bot] = injector.get(Repo[uuid.UUID, Bot])
    token = settings.DEFAULT_TG_BOT_TOKEN
    diagram_id = uuid.UUID('b9a7d66f-c0e3-4b7e-9c9b-e047b998722c')
    bot = Bot(id=uuid.uuid4(), name='test', token=token, diagram_id=diagram_id, run_on_startup=True)
    await bot_repo.create(bot)

    tg_bot_service = injector.get(TgBotService)
    await tg_bot_service.startup()
    try:
        yield
    finally:
        await tg_bot_service.shutdown()


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        diagram_repo = PickleRepo('diagram_repo.pkl')
        diagram_repo.load()
        atexit.register(diagram_repo.save)
        binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(diagram_repo), scope=singleton)
        binder.bind(Repo[uuid.UUID, Bot], to=InstanceProvider(InMemoryRepo()), scope=singleton)


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

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=8000)
