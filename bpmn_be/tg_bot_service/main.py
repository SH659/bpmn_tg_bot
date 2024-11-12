import atexit
import os.path
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
from bpmn_be.diagram_service_api_client.client import DiagramApiClient
from bpmn_be.tg_bot_service.tg_bot.schemas import CreateBot
from bpmn_be.tg_bot_service.tg_bot.service import TgBotService
from diagram.errors import BotNotFoundError
from diagram.errors import DiagramNotFoundError
from schemas import Diagram
from settings import settings
from tg_bot.schemas import Bot

configure_logging()


async def return_404(req, exc):
    raise HTTPException(status_code=404, detail="Not found")


@asynccontextmanager
async def lifespan(app: FastAPI):
    injector.binder.install(AppModule())
    bot_service = injector.get(TgBotService)
    diagram_service = DiagramApiClient(settings.DIAGRAM_SERVICE_API_URL)

    if (bot := await bot_service.get_default(error=False)) is None:
        diagram_id = (await diagram_service.get_by_name('echo_example')).id
        bot = await bot_service.create(
            CreateBot(
                name=settings.DEFAULT_BOT,
                token=settings.DEFAULT_TG_BOT_TOKEN,
                diagram_id=diagram_id,
                run_on_startup=True
            )
        )

    tg_bot_service = injector.get(TgBotService)
    await tg_bot_service.startup()
    try:
        yield
    finally:
        await tg_bot_service.shutdown()


class AppModule(Module):
    def configure(self, binder: Binder) -> None:
        # diagram_repo = PickleRepo('../backup/backup_diagram_repo.pkl')

        # diagram_repo.load()
        # atexit.register(diagram_repo.save)
        # binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(diagram_repo), scope=singleton)
        diagram_api_client = DiagramApiClient(settings.DIAGRAM_SERVICE_API_URL)
        binder.bind(DiagramApiClient, to=InstanceProvider(diagram_api_client), scope=singleton)
        bots_repo = PickleRepo(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'bots_repo.pkj'
            )
        )
        bots_repo.load()
        atexit.register(bots_repo.save)
        binder.bind(Repo[uuid.UUID, Bot], to=InstanceProvider(bots_repo), scope=singleton)


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
