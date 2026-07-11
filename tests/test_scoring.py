from neuer_radar.core.models import Article, UserProfile
from neuer_radar.core.scoring import score_article


def test_score_article_keeps_relevant_agent_content() -> None:
    profile = UserProfile(
        name="Santiago",
        role_target="AI Infrastructure Engineer",
        interests=["AI agents", "LangGraph", "DevOps automation"],
        avoid=["generic hype"],
        goals=["find remote job"],
    )
    article = Article(
        source_name="Example",
        source_category="agents",
        title="AI agents with LangGraph for DevOps automation",
        link="https://example.com/article",
        summary="A practical architecture for cloud workflows.",
    )

    scored = score_article(article, profile)

    assert scored.decision == "keep"
    assert scored.relevance_score >= 25
