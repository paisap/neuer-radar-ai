from __future__ import annotations

import os

from dotenv import load_dotenv

from neuer_radar.ai.providers.base import LLMProvider
from neuer_radar.ai.providers.ollama import OllamaProvider


def get_llm_provider(
    model: str | None = None,
) -> LLMProvider:

    load_dotenv()

    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).lower().strip()

    if provider == "ollama":
        return OllamaProvider(model=model)

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )
