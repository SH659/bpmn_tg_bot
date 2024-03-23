import atexit
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
from core.settings import Settings, settings
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
    tg_bot_service = injector.get(TgBotService)
    await tg_bot_service.startup()
    try:
        yield
    finally:
        await tg_bot_service.shutdown()


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        # binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(InMemoryRepo()), scope=singleton)
        diagram_repo = PickleRepo('diagram_repo.pkl')
        diagram_repo.load()
        atexit.register(diagram_repo.save)
        binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(diagram_repo), scope=singleton)

        token = settings.DEFAULT_TG_BOT_TOKEN
        diagram_id = uuid.UUID('b9a7d66f-c0e3-4b7e-9c9b-e047b998722c')
        bot_id = uuid.uuid4()
        bot = Bot(id=bot_id, name='test', token=token, diagram_id=diagram_id, run_on_startup=True)
        bot_repo = InMemoryRepo([bot])
        binder.bind(Repo[uuid.UUID, Bot], to=InstanceProvider(bot_repo), scope=singleton)


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
