from __future__ import annotations

import re

from neuer_radar.core.models import Article, ScoredArticle, UserProfile


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def score_article(article: Article, profile: UserProfile) -> ScoredArticle:
    text = _normalize(f"{article.title} {article.summary} {' '.join(article.tags)}")
    score = 0
    hits: list[str] = []

    for interest in profile.interests:
        normalized = _normalize(interest)
        if normalized in text:
            score += 18
            hits.append(interest)

    for avoid in profile.avoid:
        normalized = _normalize(avoid)
        if normalized in text:
            score -= 25

    if article.source_category in {"agents", "ai", "cloud", "security", "devops"}:
        score += 10

    score = max(0, min(100, score))
    decision = "keep" if score >= 25 else "skip"
    reason = "Matched: " + ", ".join(hits[:5]) if hits else "Relevant source/category heuristic"

    return ScoredArticle(
        article=article,
        relevance_score=score,
        reason=reason,
        decision=decision,
    )


def rank_articles(articles: list[Article], profile: UserProfile) -> list[ScoredArticle]:
    scored = [score_article(article, profile) for article in articles]
    return sorted(scored, key=lambda item: item.relevance_score, reverse=True)
