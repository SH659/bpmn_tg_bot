import logging
import sys

from aiogram import Bot as AiogramBot, Dispatcher, types
from aiogram.fsm.context import FSMContext

from diagram.executor.bpmn_executor import BpmnExecutor, State, Data, SendMessage, WaitMessage
from diagram.models import Diagram
from diagram.parser.bpmn_parser import xml_to_process
from tg_bot.models import Bot


async def run_diagram(bot: Bot, diagram: Diagram):
    process = xml_to_process(diagram.xml)
    executor = BpmnExecutor(process)

    dp = Dispatcher()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    @dp.message()
    async def echo(message: types.Message, state: FSMContext):
        data = await state.get_data()
        bpmn_state = State(**data['bpmn_state']) if data else State()
        res, bpmn_state = executor.step(Data(message=message.text), bpmn_state)

        for item in res:
            match item:
                case SendMessage(text):
                    await message.answer(text)
                case WaitMessage():
                    await message.answer('Waiting for your message')
                case _:
                    pass

        await state.set_data({'bpmn_state': bpmn_state.model_dump(mode='json')})

    await dp.start_polling(AiogramBot(token=bot.token))
