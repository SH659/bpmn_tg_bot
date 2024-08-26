import asyncio
import uuid

from injector import inject
from ollama import AsyncClient

from ai.context_answer import Chat, retry
from bases.pickle_repo import PickleRepo
from bases.repo import Repo
from core.di import injector
from core.settings import Settings
from diagram.executor.bpmn_executor import BpmnExecutor, State, Data
from diagram.models import Diagram
from diagram.parser.bpmn_parser import xml_to_process
from diagram.service import DiagramService
from main import AppModule
from tg_bot.service import TgBotService

injector.binder.install(AppModule())


@retry(silent=False)
async def ai_ask(
    chat: Chat,
    context: str,
    question: str,
) -> str:
    async with chat.transaction():
        res = await chat.ask(question, unpack=True)
        res = res.removesuffix('.')
        return res


@inject
async def main(
    ds: DiagramService,
    settings: Settings,
    diagram_repo: Repo[uuid.UUID, Diagram],
    bot_service: TgBotService,
):
    # diagram_repo.load()

    diagram_repo = PickleRepo('diagram_repo.pkl')
    diagram_repo.load()
    diagrams = await ds.get_all()
    print(diagrams)
    diagram = await ds.get_by_name('echo_example')
    # diagrams = await ds.get_all()
    # print(diagrams)
    bots = await bot_service.get_all()
    bots[0].diagram_id = diagram.id
    await bot_service.update(bots[0].id, bots[0])

    print(bots)

    # diagram = await ds.get_by_name('hui')
    # with open('echo_example.xml', 'w') as f:
    #     f.write(diagram.xml)
    # await diagram_repo.delete(diagram.id)
    # diagram_repo.save()
    return

    # context = 'Good evening we are from Ukraine! Im Igor, 22 years old.'
    context = 'Im Igor, 22 years old.'
    diagram = await ds.get_by_name('skip_example')
    process = xml_to_process(diagram.xml)
    executor = BpmnExecutor(process)
    state = State()
    chat = Chat(client=AsyncClient(), model=settings.CUSTOM_CHAT_MODEL)
    # chat.system(
    #     content="You are user. Act as user. Answer all questions as short as possible."
    #             "If you dont know the answer, respond with 'I dont know'"
    #             "There is your text: " + context
    # )

    action, state = await executor.step(Data('/start'), state)
    question: str = action[0].message
    print(question)

    async def ask():
        return await chat.generate(
            prompt=f'{context}'
                   f'\n'
                   f'RESPOND AS SHORT AS POSSIBLE.\n'
                   f'IF YOU DONT KNOW THE ANSWER, RESPOND WITH "I DONT KNOW".\n'
                   f'{question}',
            unpack=True
        )

    resp = await ask()
    print(resp)

    action, state = await executor.step(Data(resp), state)
    question: str = action[0].message
    print(question)
    resp: str = await ask()
    print(resp)

    action, state = await executor.step(Data(resp), state)
    question: str = action[0].message
    print(question)
    resp: str = await ask()
    print(resp)

    #
    # action, state = await executor.step(Data(resp), state)
    # question: str = action[0].message
    # print(question)
    # resp: str = await ai_ask(chat, context=context, question=question)
    # print(resp)

    # print(chat.messages)


if __name__ == '__main__':
    asyncio.run(injector.call_with_injection(main))
