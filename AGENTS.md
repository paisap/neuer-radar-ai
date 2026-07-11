# Agent Instructions

This repository is a Python project for a personal daily AI/DevOps radar.

## Agent behavior
- Work incrementally.
- Explain tradeoffs briefly.
- Run `make check` before claiming the project is healthy.
- Do not introduce AWS, Docker, RAG, or frontend until the current milestone requires it.
- Do not add secrets to the repo.

## Stack
Python 3.11+, uv, Typer, Pydantic, SQLite, pytest, Ruff, mypy, LangGraph later.

## Useful commands
```bash
uv sync --extra dev
uv run neuer-radar doctor
uv run neuer-radar run
make check
```
