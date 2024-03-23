from pprint import pprint

import xmltodict
from pydantic import BaseModel, Field


class Model(BaseModel):
    class Config:
        populate_by_name = True


class MessageEventDefinition(Model):
    id: str = Field(alias='@id')


class Event(Model):
    id: str = Field(alias='@id')
    name: str | None = Field(None, alias='@name')
    incoming: str | None = Field(None, alias='bpmn:incoming')
    outgoing: str | None = Field(None, alias='bpmn:outgoing')
    message_event_definition: MessageEventDefinition | None = Field(None, alias='bpmn:messageEventDefinition')
    type: str


class SequenceFlowItem(Model):
    id: str = Field(alias='@id')
    source_ref: str = Field(alias='@sourceRef')
    target_ref: str = Field(alias='@targetRef')


class Process(Model):
    id: str = Field(alias='@id')
    is_executable: str = Field(alias='@isExecutable')
    events: list[Event] = Field()
    sequence_flow: list[SequenceFlowItem] = Field(alias='bpmn:sequenceFlow')


def xml_to_process(xml: str) -> Process:
    process = xmltodict.parse(xml)['bpmn:definitions']['bpmn:process']
    events = []
    for key, value in process.items():
        if key.startswith('bpmn:'):
            if not isinstance(value, list):
                value = [value]
                process[key] = value

        if key.startswith('bpmn:') and key.endswith('Event'):
            for value_item in value:
                value_item['type'] = key.split(':')[-1]
            events.extend(value)
    process['events'] = events
    return Process(**process)
