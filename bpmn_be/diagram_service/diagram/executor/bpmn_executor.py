import json
from copy import deepcopy
from dataclasses import dataclass

import curlparser
import httpx
from pydantic import BaseModel, Field

from diagram.parser.bpmn_parser import Process, SequenceFlowItem, Event
from schemas import Action, SendMessage, Stop


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
            return [], state

        res = []
        event = current_event()
        while state.current_event_id:
            r = await self.execute_event(event, data, state)
            res.extend(r)
            if len(r) > 0 and isinstance(r[-1], Stop):
                res.pop()
                break
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
                    data_type = {
                        'int': int,
                        'float': float,
                        'str': str,
                    }[dt]
                    try:
                        value = data_type(data.message)
                    except ValueError as e:
                        human_readable_error = {
                            'int': 'Enter a number. Example: 123',
                            'float': 'Enter a number. Example: 123.45',
                            'str': 'Enter a string. Example: hello',
                        }
                        return [SendMessage(human_readable_error[dt]), Stop()]
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
                    print('payload', response.request.content)
                    print(f'response {response.status_code}: {response.json()}')
                    state.data['resp'] = response.json()
                    return []
            case 'task':
                key, expr = event.name.split('=')
                key = key.strip()
                expr = expr.strip()
                print('state: ', state.data)
                print('expr:', expr)
                res = eval(expr, {'json': json}, state.data)
                state.data[key] = res
                return []
            case 'endEvent':
                return []
            case _:
                print(f'Unsupported event type: {event.type}')
                raise NotImplementedError

        return []

    def get_next_event(self, state: State):
        event = self.events[state.current_event_id]
        if event.outgoing is None:
            return None
        if isinstance(event.outgoing, list) and len(event.outgoing) > 1:
            raise NotImplementedError
        flow_item = self.flow_map[event.outgoing]
        next_event = self.events[flow_item.target_ref]
        if next_event.type != 'exclusiveGateway':
            return next_event

        for out in next_event.outgoing:
            flow_item = self.flow_map[out]
            eval_res = eval(flow_item.name.format_map(state.data), {}, state.data)
            if bool(eval_res):
                next_event = self.events[flow_item.target_ref]
                return next_event
        return None

    def go_to_next_event(self, state: State):
        next_event = self.get_next_event(state)
        if next_event is None:
            state.current_event_id = None
            return
        state.current_event_id = next_event.id
        return next_event
