from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):

    @abstractmethod
    def complete_json(
        self,
        messages: list[dict[str, Any]],
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Return a parsed structured JSON response."""

    @abstractmethod
    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Allow the model to request one or more tools."""
