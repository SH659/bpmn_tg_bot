import asyncio
import logging
import sys
import traceback

from aiogram import Bot as AiogramBot, Dispatcher, types
from aiogram.fsm.context import FSMContext

from client import DiagramApiClient
from diagram.errors import ValidationError, NoResponseError
from diagram.executor.bpmn_executor import State
from schemas import SendMessage, WaitMessage
from tg_bot.schemas import Bot

logger = logging.getLogger(__name__)


async def run_diagram(tg_bot: Bot, ds: DiagramApiClient):
    bot = AiogramBot(token=tg_bot.token)

    dp = Dispatcher()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    @dp.message()
    async def echo(message: types.Message, state: FSMContext):
        await bot.send_chat_action(message.chat.id, 'typing')
        data = await state.get_data()
        bpmn_state = State(**data['bpmn_state']) if data else State()
        bpmn_state.data['user_id'] = message.from_user.id

        try:
            res = await ds.run_diagram(
                tg_bot.diagram_id,
                message.text,
                bpmn_state.model_dump()
            )
        except ValueError as e:
            traceback.print_exc()
            await message.answer('internal error')
            return
        except ValidationError as e:
            await message.answer(e.message)
            return
        except NoResponseError as e:
            return

        logger.info(f'Actions: {res.actions}')

        for action in res.actions:
            logger.info(f'Action: {action}')
            match action:
                case SendMessage(text):
                    await message.answer(text)
                case WaitMessage():
                    await message.answer('Waiting for your message')
                case _:
                    pass

        logger.info(f'New state: {res.new_state}')
        await state.set_data({'bpmn_state': res.new_state})
        logger.info(f'Processed message: {message.text}')

    task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    return dp
