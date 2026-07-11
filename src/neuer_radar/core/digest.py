from __future__ import annotations

from pathlib import Path

from neuer_radar.core.models import DailyDigest, ScoredArticle, UserProfile


def build_digest(scored_articles: list[ScoredArticle], profile: UserProfile, max_items: int = 10) -> DailyDigest:
    kept = [item for item in scored_articles if item.decision == "keep"][:max_items]
    recommendation = _build_recommendation(kept, profile)

    return DailyDigest(
        title="Neuer Radar AI - Daily Technical Brief",
        items=kept,
        recommendation=recommendation,
    )


def _build_recommendation(items: list[ScoredArticle], profile: UserProfile) -> str:
    if not items:
        return "No high-signal items found today. Improve sources or lower threshold."

    top = items[0]
    return (
        f"Focus today on: {top.article.title}. "
        f"Why: {top.reason}. Connect it to your goal: {profile.goals[0] if profile.goals else 'build useful AI automation'}."
    )


def render_markdown(digest: DailyDigest) -> str:
    lines: list[str] = []
    lines.append(f"# {digest.title}")
    lines.append("")
    lines.append(f"Generated at: `{digest.generated_at.isoformat()}`")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(digest.recommendation)
    lines.append("")
    lines.append("## Items")
    lines.append("")

    for index, item in enumerate(digest.items, start=1):
        article = item.article
        lines.append(f"### {index}. {article.title}")
        lines.append("")
        lines.append(f"- Source: `{article.source_name}` / `{article.source_category}`")
        lines.append(f"- Score: `{item.relevance_score}`")
        lines.append(f"- Reason: {item.reason}")
        lines.append(f"- Link: {article.link}")
        if article.summary:
            clean_summary = " ".join(article.summary.split())
            lines.append(f"- Raw summary: {clean_summary[:500]}")
        lines.append("")

    return "\n".join(lines)


def save_digest(markdown: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "daily-digest.md"
    target.write_text(markdown, encoding="utf-8")
    return target
