import atexit
import json
import os
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
from core.settings import settings
from diagram.errors import DiagramNotFoundError
from diagram.models import Diagram
from diagram.service import DiagramService
from tg_bot.errors import BotNotFoundError
from tg_bot.models import Bot
from tg_bot.schemas import CreateBot
from tg_bot.service import TgBotService

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

    bot_service = injector.get(TgBotService)

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
        diagram_repo = PickleRepo('diagram_repo.pkl')
        diagram_repo.load()
        atexit.register(diagram_repo.save)
        binder.bind(Repo[uuid.UUID, Diagram], to=InstanceProvider(diagram_repo), scope=singleton)

        bots_repo = PickleRepo('bots_repo.pkj')
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

    uvicorn.run('main:app', reload=True, port=8000)
