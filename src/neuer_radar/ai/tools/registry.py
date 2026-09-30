from __future__ import annotations

from typing import Any

from neuer_radar.ai.tools.github import (
    GITHUB_README_TOOL,
    get_github_readme,
)


AVAILABLE_TOOL_SCHEMAS = [
    GITHUB_README_TOOL,
]


TOOL_FUNCTIONS = {
    "get_github_readme": get_github_readme,
}


def execute_tool(
    name: str,
    arguments: dict[str, Any],
) -> str:

    print("\n========== TOOL EXECUTOR ==========")
    print(f"Requested tool: {name}")
    print(f"Arguments: {arguments}")

    function = TOOL_FUNCTIONS.get(name)

    if function is None:
        print("STATUS: REJECTED")
        print("Reason: Tool is not registered")
        print("===================================\n")

        raise ValueError(
            f"Unknown or unauthorized tool: {name}"
        )

    print("STATUS: AUTHORIZED")
    print(f"Python function: {function.__name__}")

    result = str(
        function(**arguments)
    )

    print(f"Result chars: {len(result)}")

    print("\n--- TOOL RESULT PREVIEW ---")
    print(result[:1000])

    if len(result) > 1000:
        print("\n...[truncated debug preview]")

    print("===================================\n")

    return result