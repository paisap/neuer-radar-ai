from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0


@dataclass
class ToolCallTrace:
    name: str
    arguments: dict[str, Any]
    result_preview: str | None = None
    latency_ms: float = 0.0


@dataclass
class ArticleTrace:
    title: str
    source: str
    heuristic_score: float | None = None

    initial_decision: str | None = None
    initial_relevance_score: int | None = None

    final_decision: str | None = None
    final_relevance_score: int | None = None

    prompt: str | None = None
    raw_response: str | None = None

    llm_usage: LLMUsage = field(default_factory=LLMUsage)
    tool_calls: list[ToolCallTrace] = field(default_factory=list)


@dataclass
class RunTrace:
    run_id: str
    started_at: datetime
    finished_at: datetime | None = None
    articles: list[ArticleTrace] = field(default_factory=list)
