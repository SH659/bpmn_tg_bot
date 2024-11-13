from copy import deepcopy
from dataclasses import dataclass

import curlparser
import httpx
from pydantic import BaseModel, Field

from diagram.parser.bpmn_parser import Process, SequenceFlowItem, Event
from diagram.errors import NoResponseError, ValidationError
from schemas import Action, SendMessage


@dataclass
class Data:
    message: str = None


class State(BaseModel):
    current_event_id: str | None = None
    data: dict = Field(default_factory=dict)


class BpmnExecutor:
    """
    ```
    process = Process(**process)
    executor = BpmnExecutor(process)
    gen = executor.run()

    next(gen)
    print(gen.send(Data('/start')))
    next(gen)
    ```
    """

    def __init__(self, process: Process):
        self.process = process
        self.flow_map: dict[str, SequenceFlowItem] = {f.id: f for f in process.sequence_flow}
        self.events: dict[str, Event] = {event.id: event for event in process.events}

    async def step(self, data: Data, state: State = None) -> tuple[list[Action], State]:
        state = deepcopy(state) if state is not None else State()

        def current_event() -> Event | None:
            return self.events.get(state.current_event_id)

        if data.message.startswith('/'):
            for event in self.process.events:
                if event.type == 'startEvent' and not event.name.startswith('/'):
                    state.current_event_id = event.id
                    break

        if state.current_event_id is None or state.current_event_id not in self.events:
            for event in self.process.events:
                if event.type == 'startEvent' and data.message == event.name:
                    state.current_event_id = event.id
                    break

        if state.current_event_id is None:
            for event in self.process.events:
                if event.type == 'startEvent' and ':' in event.name:
                    state.current_event_id = event.id
                    break

        if state.current_event_id is None:
            raise NoResponseError('No start event found')

        res = []
        event = current_event()
        while state.current_event_id:
            r = await self.execute_event(event, data, state)
            res.extend(r)
            self.go_to_next_event(state)
            event = current_event()
            if event is not None and event.type in (
                'intermediateCatchEvent'
            ):
                break
        return res, state

    @staticmethod
    async def execute_event(event, data, state: State) -> list[Action]:
        match event.type:
            case 'startEvent' | 'intermediateCatchEvent':
                if ':' in event.name:
                    key, dt = event.name.split(':')
                    key = key.strip()
                    dt = dt.strip()
                    dt = {
                        'int': int,
                        'float': float,
                        'str': str,
                    }[dt]
                    try:
                        value = dt(data.message)
                    except ValueError:
                        raise ValidationError('Invalid value')
                    state.data[key] = value
                return []
            case 'intermediateThrowEvent':
                message = event.name.format_map(state.data)
                return [SendMessage(message)]
            case 'serviceTask':
                curl = curlparser.parse(event.name.format_map(state.data))
                client = httpx.AsyncClient()
                async with client:
                    response = await client.request(
                        method=curl.method,
                        url=curl.url,
                        headers=curl.header,
                        data=curl.data,
                    )
                    state.data['resp'] = response.json()
                    return []
            case 'task':
                key, expr = event.name.split('=')
                key = key.strip()
                expr = expr.strip()
                state.data[key] = eval(expr.format_map(state.data), {}, state.data)
                return []

        return []

    def get_next_event(self, state: State):
        event = self.events[state.current_event_id]
        if event.outgoing is None:
            return None
        flow_item = self.flow_map[event.outgoing]
        return self.events[flow_item.target_ref]

    def go_to_next_event(self, state: State):
        event = self.events[state.current_event_id]
        if event.outgoing is None:
            state.current_event_id = None
            return
        flow_item = self.flow_map[event.outgoing]
        state.current_event_id = flow_item.target_ref
        return self.events[state.current_event_id]
