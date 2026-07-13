from __future__ import annotations

from neuer_radar.collectors.github_trending import collect_github_trending
from neuer_radar.collectors.hacker_news import collect_hacker_news
from neuer_radar.collectors.rss import collect_from_source
from neuer_radar.core.models import Article, Source


def collect_from_any_source(source: Source, limit: int = 10) -> list[Article]:
    url = str(source.url)

    if "hacker-news.firebaseio.com" in url or "news.ycombinator.com" in url:
        return collect_hacker_news(source, limit=limit)

    if "github.com/trending" in url:
        return collect_github_trending(source, limit=limit)

    return collect_from_source(source, limit=limit)


def collect_all(sources: list[Source], limit_per_source: int = 10) -> list[Article]:
    articles: list[Article] = []

    for source in sources:
        try:
            articles.extend(collect_from_any_source(source, limit=limit_per_source))
        except Exception as exc:
            print(f"[WARN] Failed source={source.name}: {exc}")

    return articles
