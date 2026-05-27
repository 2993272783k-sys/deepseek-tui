import json
import os
import httpx
from typing import AsyncIterator

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekError(Exception):
    pass


class DeepSeekClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise DeepSeekError(
                "DEEPSEEK_API_KEY 未设置。请通过环境变量或 --api-key 参数提供。"
            )
        self._client = httpx.AsyncClient(timeout=300)

    async def chat_stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        model: str = DEFAULT_MODEL,
    ) -> AsyncIterator[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            body["tools"] = tools

        try:
            async with self._client.stream(
                "POST", DEEPSEEK_API_URL, headers=headers, json=body
            ) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise DeepSeekError(
                        f"API 错误 ({response.status_code}): {text}"
                    )
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    if data:
                        yield json.loads(data)
        except httpx.TimeoutException:
            raise DeepSeekError("请求超时，请重试。")
        except httpx.RequestError as e:
            raise DeepSeekError(f"网络错误: {e}")

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        model: str = DEFAULT_MODEL,
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            body["tools"] = tools

        try:
            response = await self._client.post(
                DEEPSEEK_API_URL, headers=headers, json=body
            )
            if response.status_code != 200:
                raise DeepSeekError(
                    f"API 错误 ({response.status_code}): {response.text}"
                )
            return response.json()
        except httpx.TimeoutException:
            raise DeepSeekError("请求超时，请重试。")
        except httpx.RequestError as e:
            raise DeepSeekError(f"网络错误: {e}")

    async def close(self):
        await self._client.aclose()
