import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from textwrap import indent
from typing import Literal, Self

from ollama import AsyncClient


class ChatExplicitRollback(Exception):
    pass


def retry(retries=3, silent=True):
    def wrap(f):
        async def wrapper(*args, **kwargs):
            last_e = None
            for _ in range(retries):
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    if not silent:
                        print(f"{type(e).__name__}: {e}")
                    last_e = e
            raise last_e

        return wrapper

    return wrap


def timeout(seconds=3):
    def wrap(f):
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(f(*args, **kwargs), timeout=seconds)

        return wrapper

    return wrap


class Chat:
    def __init__(self, client: AsyncClient, model: str):
        self.client = client
        self.model = model
        self.messages = []

    @timeout(5)
    async def generate(self, /, prompt: str, format: Literal['', 'json'] = '', unpack=True, **kwargs):
        response = await self.client.generate(model=self.model, prompt=prompt, **kwargs)
        if format == 'json':
            return json.loads(response['response'])
        if unpack:
            return response['response']
        return response

    async def choice(
        self, /,
        message: str,
        options: dict[str, list[str]],
        format: Literal['', 'json'] = '',
        unpack: bool = False,
        **kwargs
    ):
        if unpack and len(options) > 1:
            raise ValueError('unpack=True can only be used when there is only one option')

        message_build = []

        if len(options) == 1:
            key = next(iter(options.keys()))
            message_build.append(f'Provide response in JSON format. Json must contain ONLY {key} key')
        else:
            message_build.append(f'Provide response in JSON format. Json must contain these keys:')
            message_build.extend(indent('\n'.join(options.keys()), prefix='- ').splitlines())

        for key, values in options.items():
            message_build.append(key)
            message_build.extend(indent('\n'.join(values), prefix='- ').splitlines())

        message_build.append(message)
        message = '\n'.join(message_build)
        res = await self.ask(message, format=format, **kwargs)
        if unpack:
            key = next(iter(options.keys()))
            return res[key]
        return res

    @timeout(5)
    async def ask(
        self, /,
        content: str = None,
        format: Literal['', 'json'] = '',
        unpack: bool = False,
        **kwargs
    ):
        if content:
            self.messages.append({'role': 'user', 'content': content})
        response = await self.client.chat(
            model=self.model,
            messages=self.messages,
            format=format,
            **kwargs
        )
        self.messages.append(response['message'])
        if format == 'json':
            return json.loads(response['message']['content'])
        if unpack:
            return response['message']['content']
        return response

    @asynccontextmanager
    async def transaction(self) -> Self:
        messages_backup = deepcopy(self.messages)
        try:
            yield self
        except ChatExplicitRollback:
            self.messages = messages_backup
        except Exception as e:
            self.messages = messages_backup
            raise e

    def rollback(self):
        raise ChatExplicitRollback

    def system(self, /, content: str):
        self.messages.append({'role': 'system', 'content': content})
