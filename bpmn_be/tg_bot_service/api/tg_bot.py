from uuid import UUID

from fastapi import APIRouter

from bpmn_be.bases.di import di
from tg_bot.schemas import Bot
from bpmn_be.tg_bot_service.tg_bot.schemas import CreateBot, UpdateBot
from bpmn_be.tg_bot_service.tg_bot.service import TgBotService

router = APIRouter()


@router.get("/", response_model=list[Bot])
async def list_bots(
    bots=di(TgBotService)
):
    return await bots.get_all()


@router.post("/", response_model=Bot)
async def create_bot(
    request: CreateBot,
    bots=di(TgBotService)
):
    return await bots.create(request)


@router.put("/assign_default/{diagram_id}")
async def assign_default_bot(
    diagram_id: UUID,
    bots=di(TgBotService)
):
    bot = await bots.get_default()
    bot.diagram_id = diagram_id
    await bots.update(bot.id, UpdateBot(diagram_id=diagram_id))


@router.get("/{bot_id}", response_model=Bot)
async def get_bot(
    bot_id: UUID,
    bots=di(TgBotService)
):
    return await bots.get_by_id(bot_id)


@router.put("/{bot_id}", response_model=Bot)
async def update_bot(
    bot_id: UUID,
    request: UpdateBot,
    bots=di(TgBotService)
):
    return await bots.update(bot_id, request)


@router.delete("/{bot_id}", response_model=Bot)
async def delete_bot(
    bot_id: UUID,
    bots=di(TgBotService)
):
    await bots.stop(bot_id)
    return await bots.delete(bot_id)


@router.post("/{bot_id}/run")
async def run_bot(
    bot_id: UUID,
    bots=di(TgBotService)
):
    await bots.run(bot_id)
    return {"status": "ok"}


@router.post("/{bot_id}/stop")
async def stop_bot(
    bot_id: UUID,
    bots=di(TgBotService)
):
    await bots.stop(bot_id)
    return {"status": "ok"}


@router.post("/{bot_id}/restart")
async def restart_bot(
    bot_id: UUID,
    bots=di(TgBotService)
):
    await bots.restart_bot(bot_id)
    return {"status": "ok"}


@router.post("/restart_by_diagram/{diagram_id}")
async def restart_bots_by_diagram_id(
    diagram_id: UUID,
    bots=di(TgBotService)
):
    await bots.restart_bots_by_diagram_id(diagram_id)
    return {"status": "ok"}
