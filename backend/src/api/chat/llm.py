"""LLM provider abstraction. Add new providers by implementing `stream`."""

from collections.abc import AsyncIterator
from typing import Protocol

from openai import AsyncOpenAI

from api.core.config import settings


class ChatTurn(Protocol):
    role: str
    content: str


class LLMProvider(Protocol):
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]: ...


class MockProvider:
    """Yields a canned response token-by-token. Useful for tests and dev without keys."""

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        last = messages[-1]["content"] if messages else ""
        reply = f"(mock) You said: {last}. Replace LLM_PROVIDER=openai for real responses."
        for tok in reply.split(" "):
            yield tok + " "


class OpenAIProvider:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore[arg-type]
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


def get_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider()
    # TODO: anthropic, ollama
    return MockProvider()
