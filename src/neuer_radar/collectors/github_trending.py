from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

from neuer_radar.core.models import Article, Source


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def collect_github_trending(source: Source, limit: int = 25) -> list[Article]:
    response = httpx.get(
        str(source.url),
        timeout=20,
        headers={
            "User-Agent": "neuer-radar-ai/0.1 (+local learning project)",
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    repo_cards = soup.select("article.Box-row")[:limit]

    articles: list[Article] = []

    for card in repo_cards:
        title_node = card.select_one("h2 a")
        if not title_node:
            continue

        repo_path = _clean_text(title_node.get_text()).replace(" / ", "/")
        repo_url = f"https://github.com{title_node.get('href')}"

        description_node = card.select_one("p")
        description = _clean_text(description_node.get_text()) if description_node else ""

        language_node = card.select_one("[itemprop='programmingLanguage']")
        language = _clean_text(language_node.get_text()) if language_node else "unknown"

        text = _clean_text(card.get_text())
        stars_today_match = re.search(r"(\d[\d,]*) stars today", text)
        stars_today = stars_today_match.group(1) if stars_today_match else "unknown"

        summary = f"GitHub Trending repo. Language: {language}. Stars today: {stars_today}. {description}"

        articles.append(
            Article(
                source_name=source.name,
                source_category=source.category,
                title=repo_path,
                link=repo_url,
                summary=summary,
                tags=[source.category, "github-trending", language.lower()],
            )
        )

    print("estos son los github")
    print(articles)
    return articles
