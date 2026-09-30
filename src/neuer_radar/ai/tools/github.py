from __future__ import annotations

from neuer_radar.enrichers.github import (
    fetch_github_readme_from_url,
)


GITHUB_README_TOOL = {
    "type": "function",
    "function": {
        "name": "get_github_readme",
        "description": (
            "Retrieve useful technical content from the "
            "README of a GitHub repository. "
            "Use this when repository metadata is not "
            "enough to determine its technical relevance."
        ),
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {
                    "type": "string",
                    "description": (
                        "Full GitHub repository URL."
                    ),
                },
            },
        },
    },
}


def get_github_readme(url: str) -> str:

    return fetch_github_readme_from_url(url)