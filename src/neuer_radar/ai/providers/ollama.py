from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Any

import httpx
from dotenv import load_dotenv

from neuer_radar.ai.providers.base import LLMProvider


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower().strip() in {"1", "true", "yes", "on"}


def _env_optional_int(name: str) -> int | None:
    value = os.getenv(name)

    if not value:
        return None

    return int(value)


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str
    model: str
    temperature: float
    timeout: float
    think: bool
    debug: bool
    keep_alive: str
    num_ctx: int | None
    seed: int | None

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        load_dotenv()

        return cls(
            base_url=os.getenv(
                "LLM_BASE_URL",
                "http://localhost:11434",
            ).rstrip("/"),
            model=os.getenv(
                "LLM_MODEL",
                "qwen3.5:9b",
            ),
            temperature=float(
                os.getenv("LLM_TEMPERATURE", "0.9")
            ),
            timeout=float(
                os.getenv("LLM_TIMEOUT", "90")
            ),
            think=_env_bool(
                "LLM_THINK",
                False,
            ),
            debug=_env_bool(
                "LLM_DEBUG",
                True,
            ),
            keep_alive=os.getenv(
                "LLM_KEEP_ALIVE",
                "5m",
            ),
            num_ctx=_env_optional_int(
                "LLM_NUM_CTX"
            ),
            seed=_env_optional_int(
                "LLM_SEED"
            ),
        )


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str | None = None,
        config: OllamaConfig | None = None,
    ) -> None:
        self.config = config or OllamaConfig.from_env()

        # Permite que en el futuro podamos hacer:
        # OllamaProvider(model="modelo-A")
        # OllamaProvider(model="modelo-B")
        self.model = model or self.config.model

    def complete_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
    ) -> dict[str, Any]:

        request_payload = self._build_payload(
            messages=messages,
            schema=schema,
        )

        if self.config.debug:
            self._debug_request(
                messages=messages,
                payload=request_payload,
            )

        started_at = perf_counter()

        try:
            response = httpx.post(
                f"{self.config.base_url}/api/chat",
                json=request_payload,
                timeout=self.config.timeout,
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "Ollama returned an HTTP error "
                f"{exc.response.status_code}: "
                f"{exc.response.text[:1000]}"
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not connect to Ollama at "
                f"{self.config.base_url}: {exc}"
            ) from exc

        elapsed_seconds = perf_counter() - started_at

        try:
            response_payload = response.json()
        except ValueError as exc:
            raise ValueError(
                f"Ollama returned non-JSON response: "
                f"{response.text[:1000]}"
            ) from exc

        if self.config.debug:
            self._debug_response(
                response_payload,
                elapsed_seconds,
            )

        return self._parse_content(response_payload)

    def _build_payload(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
    ) -> dict[str, Any]:

        options: dict[str, Any] = {
            "temperature": self.config.temperature,
        }

        if self.config.num_ctx is not None:
            options["num_ctx"] = self.config.num_ctx

        if self.config.seed is not None:
            options["seed"] = self.config.seed

        return {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": self.config.think,
            "format": schema,
            "keep_alive": self.config.keep_alive,
            "options": options,
        }

    def _parse_content(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        content = (
            payload
            .get("message", {})
            .get("content", "")
        )

        if not content:
            raise ValueError(
                f"Ollama returned empty content: {payload}"
            )

        try:
            return json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Ollama returned invalid JSON: {content}"
            ) from exc

    def _debug_request(
        self,
        messages: list[dict[str, str]],
        payload: dict[str, Any],
    ) -> None:

        prompt_chars = sum(
            len(message.get("content", ""))
            for message in messages
        )

        options = payload["options"]

        print("\n========== OLLAMA REQUEST ==========")
        print(f"Endpoint: {self.config.base_url}/api/chat")
        print(f"Model: {self.model}")
        print(f"Messages: {len(messages)}")
        print(f"Prompt chars: {prompt_chars}")
        print(
            f"Temperature: "
            f"{options.get('temperature')}"
        )
        print(
            f"Context window requested: "
            f"{options.get('num_ctx', 'Ollama/model default')}"
        )
        print(
            f"Seed: "
            f"{options.get('seed', 'default')}"
        )
        print(f"Think: {self.config.think}")
        print(f"Keep alive: {self.config.keep_alive}")
        print(
            "Schema fields: "
            f"{', '.join(payload['format'].get('required', []))}"
        )
        print("====================================\n")

    def _debug_response(
        self,
        payload: dict[str, Any],
        elapsed_seconds: float,
    ) -> None:

        total_duration = (
            payload.get("total_duration", 0) / 1_000_000_000
        )

        load_duration = (
            payload.get("load_duration", 0) / 1_000_000_000
        )

        prompt_tokens = payload.get(
            "prompt_eval_count",
            0,
        )

        output_tokens = payload.get(
            "eval_count",
            0,
        )

        eval_duration = (
            payload.get("eval_duration", 0)
            / 1_000_000_000
        )

        tokens_per_second = (
            output_tokens / eval_duration
            if eval_duration > 0
            else 0
        )

        thinking = (
            payload
            .get("message", {})
            .get("thinking", "")
        )

        print("\n========== OLLAMA RESPONSE =========")
        print(f"Model used: {payload.get('model')}")
        print(f"Done: {payload.get('done')}")
        print(
            f"Done reason: "
            f"{payload.get('done_reason')}"
        )

        print("")
        print("--- TOKENS ---")
        print(f"Input tokens: {prompt_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(
            f"Total tokens: "
            f"{prompt_tokens + output_tokens}"
        )

        print("")
        print("--- PERFORMANCE ---")
        print(
            f"Application elapsed: "
            f"{elapsed_seconds:.2f}s"
        )
        print(
            f"Ollama total duration: "
            f"{total_duration:.2f}s"
        )
        print(
            f"Model load duration: "
            f"{load_duration:.2f}s"
        )
        print(
            f"Generation speed: "
            f"{tokens_per_second:.2f} tok/s"
        )

        print("")
        print("--- THINKING ---")
        print(
            "Thinking returned: "
            f"{'yes' if thinking else 'no'}"
        )

        print("====================================\n")
