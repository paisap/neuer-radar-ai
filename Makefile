.PHONY: install run doctor test lint format typecheck check

install:
	uv sync --extra dev

run:
	uv run neuer-radar run

doctor:
	uv run neuer-radar doctor

test:
	uv run pytest

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

typecheck:
	uv run mypy src

check: lint typecheck test
