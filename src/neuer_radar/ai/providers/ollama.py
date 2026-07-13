from __future__ import annotations

import json
import os
from typing import Any

import httpx
from dotenv import load_dotenv

from neuer_radar.ai.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        load_dotenv()

        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "qwen3.5:9b")

    def complete_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "think": False,
                "format": schema,
                "options": {
                    "temperature": 0.1,
                },
            },
            timeout=90,
        )

        response.raise_for_status()
        payload = response.json()

        content = payload.get("message", {}).get("content", "")

        if not content:
            raise ValueError(f"Ollama returned empty content: {payload}")

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Ollama returned invalid JSON: {content}") from exc
