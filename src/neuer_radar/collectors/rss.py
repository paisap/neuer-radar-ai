from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser

from neuer_radar.core.models import Article, Source


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None


def collect_from_source(source: Source, limit: int = 5) -> list[Article]:
    feed = feedparser.parse(str(source.url))
    articles: list[Article] = []

    for entry in feed.entries[:limit]:
        published = getattr(entry, "published", None) or getattr(entry, "updated", None)
        articles.append(
            Article(
                source_name=source.name,
                source_category=source.category,
                title=getattr(entry, "title", "Untitled"),
                link=getattr(entry, "link", ""),
                published_at=_parse_date(published),
                summary=getattr(entry, "summary", ""),
                tags=[source.category],
            )
        )

    return articles


def collect_all(sources: list[Source], limit_per_source: int = 5) -> list[Article]:
    articles: list[Article] = []
    for source in sources:
        try:
            articles.extend(collect_from_source(source, limit=limit_per_source))
        except Exception as exc:  # noqa: BLE001 - first MVP should keep running per source
            print(f"[WARN] Failed source={source.name}: {exc}")
    return articles
