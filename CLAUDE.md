# Claude Code Instructions

You are helping build Neuer Radar AI, a personal AI/DevOps signal radar.

## Project goal
Build a practical, portfolio-worthy Python project that collects technical sources, scores relevance against a user profile, generates a daily digest, and evolves into a LangGraph agent with memory, RAG, feedback, and later AWS deployment.

## Current phase
Phase 0: local project foundation.
Do not add cloud infrastructure, vector databases, or paid model calls unless explicitly requested.

## Engineering rules
- Keep changes small and testable.
- Prefer Python 3.11+, uv, Typer, Pydantic, SQLite, pytest, Ruff, mypy.
- Keep source code under `src/neuer_radar`.
- Add or update tests for behavior changes.
- Never commit `.env`, API keys, tokens, local DB files, or generated digests.
- Favor readable code over clever abstractions.

## Commands
- Install: `uv sync --extra dev`
- Run app: `uv run neuer-radar run`
- Doctor: `uv run neuer-radar doctor`
- Test: `uv run pytest`
- Full check: `make check`

## Next planned milestones
1. Connect first LLM provider.
2. Replace heuristic scoring with model-assisted classification.
3. Introduce LangGraph nodes: collect, score, summarize, digest, persist.
4. Add user feedback: useful / not useful / deep dive.
5. Add memory and RAG over historical digests.
