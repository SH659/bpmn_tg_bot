from copy import deepcopy
from dataclasses import dataclass

from pydantic import BaseModel, Field

from diagram.parser.bpmn_parser import Process, SequenceFlowItem, Event


@dataclass
class Data:
    message: str = None


class Action:
    pass


@dataclass
class SendMessage(Action):
    message: str


@dataclass
class WaitMessage(Action):
    pass


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

    def step(self, data: Data, state: State = None) -> tuple[list[Action], State]:
        state = deepcopy(state) if state is not None else State()
        if state.current_event_id is None or state.current_event_id not in self.events:
            for event in self.process.events:
                if event.type == 'startEvent' and data.message == event.name:
                    state.current_event_id = event.id
                    break
            else:
                for event in self.process.events:
                    if event.type == 'startEvent' and not event.name.startswith('/'):
                        state.current_event_id = event.id
                        break
                else:
                    raise ValueError('No start event found')

        res = []
        while True:
            event = self.events[state.current_event_id]
            r, should_continue = self.execute_event(event, data, state)
            res.extend(r)
            self.go_to_next_event(state)
            if not should_continue:
                break
        return res, state

    @staticmethod
    def execute_event(event, data, state: State) -> tuple[list[Action], bool]:
        match event.type:
            case 'startEvent':
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
                        return [SendMessage('Invalid value')], False
                    state.data[key] = value
                return [], True
            case 'intermediateThrowEvent':
                message = event.name.format_map(state.data)
                return [SendMessage(message)], True
            case 'intermediateCatchEvent':
                return [WaitMessage()], False
        return [], False

    def go_to_next_event(self, state: State):
        event = self.events[state.current_event_id]
        if event.outgoing is None:
            state.current_event_id = None
            return
        flow_item = self.flow_map[event.outgoing]
        state.current_event_id = flow_item.target_ref
        return self.events[state.current_event_id]
