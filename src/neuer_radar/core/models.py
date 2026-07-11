from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Source(BaseModel):
    name: str
    url: HttpUrl
    category: str = "general"


class UserProfile(BaseModel):
    name: str
    role_target: str
    interests: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)


class Article(BaseModel):
    source_name: str
    source_category: str
    title: str
    link: str
    published_at: datetime | None = None
    summary: str = ""
    tags: list[str] = Field(default_factory=list)


class ScoredArticle(BaseModel):
    article: Article
    relevance_score: int = Field(ge=0, le=100)
    reason: str
    decision: Literal["keep", "skip"]


class DailyDigest(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: str
    items: list[ScoredArticle]
    recommendation: str
