from __future__ import annotations

import typer
from rich.console import Console

from neuer_radar.collectors.router import collect_all
from neuer_radar.core.config_loader import load_profile, load_sources
from neuer_radar.core.digest import build_digest, render_markdown, save_digest
from neuer_radar.core.scoring import rank_articles
from neuer_radar.core.settings import settings
from neuer_radar.storage.sqlite import save_scored_articles
from neuer_radar.ai.classifier import refine_articles_with_ai

app = typer.Typer(help="Neuer Radar AI - personal daily signal collector")
console = Console()


@app.command()
def run(limit_per_source: int = 5, max_items: int = 10) -> None:
    """Collect RSS articles, score them, persist them, and generate a Markdown digest."""
    profile = load_profile(settings.radar_profile_path)
    sources = load_sources(settings.radar_sources_path)

    console.print(f"[bold]Loaded profile:[/bold] {profile.name}")
    console.print(f"[bold]Sources:[/bold] {len(sources)}")

    articles = collect_all(sources, limit_per_source=limit_per_source)
    # scored = rank_articles(articles, profile)
    # save_scored_articles(settings.radar_db_path, scored)
    scored = rank_articles(articles, profile)

    scored = refine_articles_with_ai(
        scored,
        profile,
    )
    print("\n============ FINAL DECISIONS =============")

    for item in scored:
        print(
            f"{item.decision.upper():5} | "
            f"{item.relevance_score:3} | "
            f"{item.article.title}"
        )

    print("==========================================\n")

    save_scored_articles(settings.radar_db_path, scored)

    digest = build_digest(scored, profile, max_items=max_items)
    markdown = render_markdown(digest)
    output_path = save_digest(markdown, settings.radar_output_dir)

    console.print(f"[green]Digest generated:[/green] {output_path}")
    console.print(f"[green]Articles collected:[/green] {len(articles)}")
    console.print(f"[green]Items kept:[/green] {len(digest.items)}")


@app.command()
def doctor() -> None:
    """Validate basic local project configuration."""
    profile = load_profile(settings.radar_profile_path)
    sources = load_sources(settings.radar_sources_path)
    console.print("[green]Configuration OK[/green]")
    console.print(f"Profile: {profile.name}")
    console.print(f"Sources: {len(sources)}")
    console.print(f"DB path: {settings.radar_db_path}")
    console.print(f"Output dir: {settings.radar_output_dir}")
