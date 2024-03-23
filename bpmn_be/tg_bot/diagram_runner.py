import asyncio
import logging
import sys
import traceback

from aiogram import Bot as AiogramBot, Dispatcher, types
from aiogram.fsm.context import FSMContext

from diagram.executor.bpmn_executor import BpmnExecutor, State, Data, SendMessage, WaitMessage
from diagram.models import Diagram
from diagram.parser.bpmn_parser import xml_to_process
from tg_bot.models import Bot


async def run_diagram(tg_bot: Bot, diagram: Diagram):
    process = xml_to_process(diagram.xml)
    executor = BpmnExecutor(process)
    bot = AiogramBot(token=tg_bot.token)

    dp = Dispatcher()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    @dp.message()
    async def echo(message: types.Message, state: FSMContext):
        await bot.send_chat_action(message.chat.id, 'typing')
        data = await state.get_data()
        bpmn_state = State(**data['bpmn_state']) if data else State()

        try:
            res, bpmn_state = executor.step(Data(message=message.text), bpmn_state)
        except ValueError as e:
            traceback.print_exc()
            await message.answer('internal error')
            return

        for item in res:
            match item:
                case SendMessage(text):
                    await message.answer(text)
                case WaitMessage():
                    await message.answer('Waiting for your message')
                case _:
                    pass

        await state.set_data({'bpmn_state': bpmn_state.model_dump(mode='json')})

    task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    return dp
