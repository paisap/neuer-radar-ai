from __future__ import annotations

import sqlite3
from pathlib import Path

from neuer_radar.core.models import Article, ScoredArticle


SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    link TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_category TEXT NOT NULL,
    title TEXT NOT NULL,
    published_at TEXT,
    summary TEXT,
    relevance_score INTEGER,
    reason TEXT,
    decision TEXT,
    inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_scored_article(db_path: Path, scored: ScoredArticle) -> None:
    article: Article = scored.article
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO articles (
                link, source_name, source_category, title, published_at, summary,
                relevance_score, reason, decision
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(link) DO UPDATE SET
                relevance_score=excluded.relevance_score,
                reason=excluded.reason,
                decision=excluded.decision
            """,
            (
                article.link,
                article.source_name,
                article.source_category,
                article.title,
                article.published_at.isoformat() if article.published_at else None,
                article.summary,
                scored.relevance_score,
                scored.reason,
                scored.decision,
            ),
        )


def save_scored_articles(db_path: Path, items: list[ScoredArticle]) -> None:
    init_db(db_path)
    for item in items:
        upsert_scored_article(db_path, item)
