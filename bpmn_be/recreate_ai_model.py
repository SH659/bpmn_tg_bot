import asyncio

from ollama import AsyncClient

from ai.modelfile import recreate, assemble_model_file
from core.settings import Settings


async def main():
    client = AsyncClient()
    settings = Settings()
    await recreate(
        client,
        assemble_model_file(settings.DEFAULT_CHAT_MODEL),
        settings.CUSTOM_CHAT_MODEL
    )


if __name__ == '__main__':
    asyncio.run(main())
