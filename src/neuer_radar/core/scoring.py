from __future__ import annotations

import re

from neuer_radar.core.models import Article, ScoredArticle, UserProfile

KEEP_THRESHOLD = 18

CATEGORY_BONUS = {
    "agents": 10,
    "ai": 10,
    "cloud": 10,
    "security": 10,
    "devops": 10,
    "hacker-news": 6,
    "github-trending": 6,
}

TECH_KEYWORDS = {
    "agent": 10,
    "agents": 10,
    "ai": 8,
    "llm": 10,
    "rag": 10,
    "langgraph": 15,
    "langchain": 12,
    "mcp": 10,
    "python": 8,
    "aws": 10,
    "devops": 10,
    "terraform": 10,
    "kubernetes": 10,
    "k8s": 10,
    "cloud": 8,
    "infrastructure": 8,
    "platform": 7,
    "security": 8,
    "observability": 8,
    "automation": 8,
    "backend": 6,
    "openai": 8,
    "anthropic": 8,
    "github": 5,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def score_article(article: Article, profile: UserProfile) -> ScoredArticle:
    text = _normalize(f"{article.title} {article.summary} {' '.join(article.tags)}")
    

    score = 0
    hits: list[str] = []
    penalties: list[str] = []

    for interest in profile.interests:
        normalized = _normalize(interest)
        if normalized and normalized in text:
            score += 18
            hits.append(interest)

    for keyword, points in TECH_KEYWORDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            score += points
            hits.append(keyword)

    category_bonus = CATEGORY_BONUS.get(article.source_category, 0)
    if category_bonus:
        score += category_bonus
        hits.append(f"source:{article.source_category}")

    for avoid in profile.avoid:
        normalized = _normalize(avoid)
        if normalized and normalized in text:
            score -= 25
            penalties.append(avoid)

    score = max(0, min(100, score))
    decision = "keep" if score >= KEEP_THRESHOLD else "skip"

    if hits:
        reason = "Matched: " + ", ".join(dict.fromkeys(hits[:8]))
    else:
        reason = "No strong match against current profile"

    if penalties:
        reason += ". Penalized: " + ", ".join(penalties[:5])

    return ScoredArticle(
        article=article,
        relevance_score=score,
        reason=reason,
        decision=decision,
    )


def rank_articles(articles: list[Article], profile: UserProfile) -> list[ScoredArticle]:
    scored = [score_article(article, profile) for article in articles]
    return sorted(scored, key=lambda item: item.relevance_score, reverse=True)
