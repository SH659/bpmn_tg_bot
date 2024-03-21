import asyncio
import uuid
from uuid import UUID

from injector import inject

from bases.repo import Repo
from diagram.service import DiagramService
from tg_bot.diagram_runner import run_diagram
from tg_bot.models import Bot
from tg_bot.schemas import CreateBot, UpdateBot


class TgBotService:
    @inject
    def __init__(
        self,
        bot_repo: Repo[UUID, Bot],
        diagram_service: DiagramService
    ):
        self.bot_repo = bot_repo
        self.diagram_service = diagram_service
        self.running = {}

    async def create(self, request: CreateBot):
        diagram = await self.diagram_service.get_by_id(request.diagram_id)
        bot = Bot(
            id=uuid.uuid4(),
            name=request.name,
            token=request.token,
            diagram_id=diagram.id
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
        await self.bot_repo.update(bot)
        return bot

    async def delete(self, bot_id: UUID):
        bot = await self.bot_repo.get_by_id(bot_id)
        await self.bot_repo.delete(bot.id)
        return bot

    async def run(self, bot_id: UUID):
        bot = await self.bot_repo.get_by_id(bot_id)
        diagram = await self.diagram_service.get_by_id(bot.diagram_id)
        self.running[bot.id] = asyncio.create_task(run_diagram(bot, diagram))

    async def shutdown(self):
        for task in self.running.values():
            task.cancel()
        self.running.clear()
