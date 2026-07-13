from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from neuer_radar.core.models import Article, Source

HN_BASE_URL = "https://hacker-news.firebaseio.com/v0"

# filtrar solo los post de las ultimas 24 horas

def _fetch_json(url: str) -> Any:
    response = httpx.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def collect_hacker_news(source: Source, limit: int = 30) -> list[Article]:
    story_ids = _fetch_json(f"{HN_BASE_URL}/newstories.json")[:limit]
    articles: list[Article] = []

    for story_id in story_ids:
        item = _fetch_json(f"{HN_BASE_URL}/item/{story_id}.json")

        if not item or item.get("type") != "story":
            continue

        title = item.get("title")
        if not title:
            continue

        link = item.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        score = item.get("score", 0)
        comments = item.get("descendants", 0)
        author = item.get("by", "unknown")
        timestamp = item.get("time")

        published_at = None
        if timestamp:
            published_at = datetime.fromtimestamp(timestamp, tz=UTC)

        summary = f"HN story by {author}. Score: {score}. Comments: {comments}."

        articles.append(
            Article(
                source_name=source.name,
                source_category=source.category,
                title=title,
                link=link,
                published_at=published_at,
                summary=summary,
                tags=[source.category, "hacker-news"],
            )
        )

    print("estos son los hacker new")
    print(articles)
    return articles
