import uuid
from uuid import UUID

from aiogram import Dispatcher
from injector import inject, singleton

from bpmn_be.bases.repo import Repo
from bpmn_be.diagram_service_api_client.client import DiagramApiClient
from ..settings import Settings
from bpmn_be.tg_bot_service.tg_bot.diagram_runner import run_diagram
from diagram.errors import BotNotFoundError
from tg_bot.schemas import Bot
from bpmn_be.tg_bot_service.tg_bot.schemas import CreateBot, UpdateBot


@singleton
class TgBotService:
    @inject
    def __init__(
        self,
        bot_repo: Repo[UUID, Bot],
        diagram_service: DiagramApiClient,
        settings: Settings
    ):
        self.bot_repo = bot_repo
        self.diagram_service = diagram_service
        self.running: dict[UUID, Dispatcher] = {}
        self.settings = settings

    async def get_default(self, error: bool = True):
        bots = await self.bot_repo.get_all()
        for bot in bots:
            if bot.name == self.settings.DEFAULT_BOT:
                return bot
        if error:
            raise BotNotFoundError

    async def get_all(self):
        return await self.bot_repo.get_all()

    async def create(self, request: CreateBot) -> Bot:
        diagram = await self.diagram_service.get_by_id(request.diagram_id)
        bot = Bot(
            id=uuid.uuid4(),
            name=request.name,
            token=request.token,
            diagram_id=diagram.id,
            run_on_startup=request.run_on_startup
        )
        await self.bot_repo.create(bot)
        return bot

    async def update(self, bot_id: UUID, request: UpdateBot):
        bot = await self.bot_repo.get_by_id(bot_id)
        if request.name:
            bot.name = request.name
        if request.token:
            bot.token = request.token
        if request.diagram_id:
            diagram = await self.diagram_service.get_by_id(request.diagram_id)
            bot.diagram_id = diagram.id
        if request.run_on_startup:
            bot.run_on_startup = request.run_on_startup
        await self.bot_repo.update(bot)
        return bot

    async def delete(self, bot_id: UUID):
        bot = await self.bot_repo.get_by_id(bot_id)
        await self.bot_repo.delete(bot.id)
        return bot

    async def get_by_id(self, bot_id: UUID):
        return await self.bot_repo.get_by_id(bot_id)

    async def run(self, bot_id: UUID):
        bot = await self.bot_repo.get_by_id(bot_id)
        self.running[bot.id] = await run_diagram(bot, self.diagram_service)

    async def stop(self, bot_id: UUID):
        dp: Dispatcher = self.running.get(bot_id)
        if dp:
            await dp.stop_polling()
            del self.running[bot_id]

    async def restart_bot(self, bot_id: UUID):
        await self.stop(bot_id)
        await self.run(bot_id)

    async def restart_bots_by_diagram_id(self, diagram_id: UUID):
        bots = await self.bot_repo.get_all()
        for bot in bots:
            if bot.diagram_id == diagram_id:
                await self.restart_bot(bot.id)

    async def startup(self):
        bots = await self.bot_repo.get_all()
        for bot in bots:
            if bot.run_on_startup:
                await self.run(bot.id)

    async def shutdown(self):
        for dp in self.running.values():
            await dp.stop_polling()
