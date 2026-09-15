from __future__ import annotations

from urllib.request import Request, urlopen

from neuer_radar.core.models import Article, ScoredArticle
import html
import re


MAX_README_CHARS = 4000


def _github_repo_from_url(url: str) -> tuple[str, str] | None:
    parts = url.rstrip("/").split("/")

    if len(parts) < 5 or "github.com" not in url:
        return None

    return parts[-2], parts[-1]


def fetch_github_readme(article: Article) -> str:
    repo = _github_repo_from_url(article.link)

    if not repo:
        return ""

    owner, name = repo

    for branch in ("main", "master"):
        raw_url = (
            f"https://raw.githubusercontent.com/"
            f"{owner}/{name}/{branch}/README.md"
        )

        try:
            request = Request(
                raw_url,
                headers={"User-Agent": "Neuer-Radar-AI"},
            )

            with urlopen(request, timeout=8) as response:
                content = response.read().decode("utf-8", errors="ignore")
                clean_content = _clean_readme(content)
                print(f"Raw README chars: {len(content)}")
                print(f"Clean README chars: {len(clean_content)}")

            return clean_content[:MAX_README_CHARS]

        except Exception:
            continue

    return ""


def enrich_candidates(
    scored_articles: list[ScoredArticle],
) -> list[ScoredArticle]:

    for item in scored_articles:

        # Solo enriquecemos artículos que sobrevivieron
        # al filtro barato.
        if item.decision == "skip":
            continue

        if item.article.source_category == "github-trending":
            item.article.content_excerpt = fetch_github_readme(
                item.article
            )

            print("\n========= ENRICHMENT =========")
            print(item.article.title)
            print(
                f"README chars: "
                f"{len(item.article.content_excerpt)}"
            )
            print("==============================\n")

    return scored_articles

def _clean_readme(content: str) -> str:
    # Eliminar imágenes Markdown: ![alt](url)
    content = re.sub(
        r"!\[[^\]]*\]\([^)]+\)",
        "",
        content,
    )

    # Eliminar bloques HTML completos que suelen ser badges/layout
    content = re.sub(
        r"<(div|p|picture)[^>]*>.*?</\1>",
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Eliminar tags HTML restantes, conservando el texto interior
    content = re.sub(
        r"<[^>]+>",
        "",
        content,
    )

    # Convertir &amp; etc.
    content = html.unescape(content)

    # Demasiados saltos de línea
    content = re.sub(
        r"\n{3,}",
        "\n\n",
        content,
    )

    return content.strip()