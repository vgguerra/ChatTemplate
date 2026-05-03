"""LLM provider abstraction. Add new providers by implementing `stream`."""

import json
from collections.abc import AsyncIterator
from typing import Protocol

import httpx
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from api.core.config import settings


class ChatTurn(Protocol):
    role: str
    content: str


class LLMProvider(Protocol):
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]: ...


def _split_system(messages: list[dict[str, str]]) -> tuple[str | None, list[dict[str, str]]]:
    """Anthropic takes `system` as a top-level field, not a message role."""
    system: str | None = None
    rest: list[dict[str, str]] = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"] if system is None else f"{system}\n\n{m['content']}"
        else:
            rest.append(m)
    return system, rest


class MockProvider:
    """Yields a canned response token-by-token. Useful for tests and dev without keys."""

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        last = messages[-1]["content"] if messages else ""
        reply = (
            f"(mock) You said: {last}. "
            "Set LLM_PROVIDER to openai/anthropic/ollama for real responses."
        )
        for tok in reply.split(" "):
            yield tok + " "


class OpenAIProvider:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
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


class AnthropicProvider:
    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        system, history = _split_system(messages)
        kwargs: dict = {
            "model": self.model,
            "messages": history,
            "max_tokens": self.max_tokens,
        }
        if system is not None:
            kwargs["system"] = system
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text


class OllamaProvider:
    """Streams from a local Ollama instance. No API key needed."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        payload = {"model": self.model, "messages": messages, "stream": True}
        async with (
            httpx.AsyncClient(timeout=httpx.Timeout(None, connect=10.0)) as client,
            client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("message", {}).get("content")
                if delta:
                    yield delta
                if chunk.get("done"):
                    break


def get_provider() -> LLMProvider:
    match settings.llm_provider:
        case "openai":
            return OpenAIProvider()
        case "anthropic":
            return AnthropicProvider()
        case "ollama":
            return OllamaProvider()
        case _:
            return MockProvider()
