"""
title: ThinkFlow
author: Weilv
author_url: https://github.com/Weilv-D/ThinkFlow
version: 1.0
license: MIT
"""

import json
import asyncio
import httpx
from typing import AsyncGenerator
from pydantic import BaseModel, Field

DATA_PREFIX = "data: "


class Pipe:
    class Valves(BaseModel):
        # R1 Reasoning Configuration
        REASONING_API_BASE: str = Field(
            default="https://api.deepseek.com", description="R1 API address"
        )
        REASONING_API_KEY: str = Field(
            default="",
            description="R1 API key",
            json_schema_extra={"format": "password"},
        )
        REASONING_MODEL: str = Field(
            default="deepseek-reasoner", description="R1 model name"
        )
        REASONING_TEMPERATURE: float = Field(
            default=0.3, description="R1 temperature parameter", ge=0.0, le=2.0
        )

        # V3 Response Configuration
        RESPONSE_API_BASE: str = Field(
            default="https://api.deepseek.com", description="V3 API address"
        )
        RESPONSE_API_KEY: str = Field(
            default="",
            description="V3 API key",
            json_schema_extra={"format": "password"},
        )
        RESPONSE_MODEL: str = Field(default="deepseek-chat", description="V3 model name")
        RESPONSE_TEMPERATURE: float = Field(
            default=0.7, description="V3 temperature parameter", ge=0.0, le=2.0
        )

    def __init__(self):
        self.valves = self.Valves()
        self.thinking_content = ""
        self.v3_response = ""

    async def pipe(self, body: dict) -> AsyncGenerator[str, None]:
        """Main processing pipeline: R1 reasoning -> V3 response"""
        yield "<think>\n"
        async for chunk in self._process_r1(body):
            yield chunk
        yield "\n</think>\n"

        v3_body = self._build_v3_body(body)
        async for chunk in self._process_v3(v3_body):
            yield chunk

    async def _process_r1(self, body: dict) -> AsyncGenerator[str, None]:
        """Process the streaming response of R1 and extract reasoning_content"""
        config = self._get_r1_config()
        payload = self._build_r1_payload(body)

        async with httpx.AsyncClient(http2=True) as client:
            async with client.stream(
                "POST",
                f"{config['base']}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {config['key']}"},
                timeout=30,
            ) as response:
                async for line in response.aiter_lines():
                    if not line.startswith(DATA_PREFIX):
                        continue

                    try:
                        data = json.loads(line[len(DATA_PREFIX):])
                        delta = data.get("choices", [{}])[0].get("delta", {})

                        if reasoning := delta.get("reasoning_content"):
                            self.thinking_content += reasoning
                            yield reasoning

                    except json.JSONDecodeError:
                        continue

    async def _process_v3(self, body: dict) -> AsyncGenerator[str, None]:
        """Process the streaming response of V3"""
        config = self._get_v3_config()
        payload = self._build_v3_payload(body)

        async with httpx.AsyncClient(http2=True) as client:
            async with client.stream(
                "POST",
                f"{config['base']}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {config['key']}"},
                timeout=30,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith(DATA_PREFIX):
                        try:
                            data = json.loads(line[len(DATA_PREFIX):])
                            if content := data["choices"][0]["delta"].get("content"):
                                self.v3_response += content
                                yield content
                        except (KeyError, json.JSONDecodeError):
                            continue

    def _build_v3_body(self, original_body: dict) -> dict:
        """Build the request body for V3 and inject reasoning_content"""
        return {
            "messages": original_body["messages"]
            + [{"role": "assistant", "content": self.thinking_content}],
            "temperature": self.valves.RESPONSE_TEMPERATURE,
        }

    def _get_r1_config(self) -> dict:
        return {
            "base": self.valves.REASONING_API_BASE,
            "key": self.valves.REASONING_API_KEY,
            "model": self.valves.REASONING_MODEL,
        }

    def _get_v3_config(self) -> dict:
        return {
            "base": self.valves.RESPONSE_API_BASE,
            "key": self.valves.RESPONSE_API_KEY,
            "model": self.valves.RESPONSE_MODEL,
        }

    def _build_r1_payload(self, body: dict) -> dict:
        return {
            "model": self.valves.REASONING_MODEL,
            "messages": body["messages"],
            "temperature": self.valves.REASONING_TEMPERATURE,
            "stream": True,
        }

    def _build_v3_payload(self, body: dict) -> dict:
        return {
            "model": self.valves.RESPONSE_MODEL,
            "messages": body["messages"],
            "temperature": body.get("temperature", 0.7),
            "stream": True,
        }

