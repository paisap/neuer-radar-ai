# Neuer Radar AI

Personal daily radar for AI, DevOps, cloud, agents, security, and remote-work signals.

The first version is intentionally local and simple: collect RSS feeds, score them against a personal profile, save articles to SQLite, and generate a Markdown digest.

## Why this project exists

This project is both useful and portfolio-oriented. It helps Santiago stay current in AI + DevOps while learning the technologies required for AI infrastructure and agentic automation roles.

## Current architecture

```text
RSS Sources -> Collector -> Relevance Scoring -> SQLite -> Markdown Digest
```

Later phases will add:

```text
LangGraph -> LLM Classification -> Summarization -> Feedback -> Memory -> RAG -> AWS Deployment
```

## Requirements

- Python 3.11+
- uv
- Git

## Setup

```bash
uv sync --extra dev
cp .env.example .env
uv run neuer-radar doctor
```

## Run

```bash
uv run neuer-radar run
```

The digest is generated at:

```text
digests/daily-digest.md
```

## Developer commands

```bash
make doctor
make run
make test
make lint
make typecheck
make check
```

## Project structure

```text
src/neuer_radar/
  collectors/       RSS and web collectors
  core/             models, scoring, digest generation
  storage/          SQLite persistence
  cli/              Typer command line app
config/             sources and personal profile
tests/              automated tests
docs/               architecture notes
```

## Roadmap

### Phase 0 - Foundation

- Clean Python project
- CLI
- RSS collector
- Relevance scoring
- SQLite persistence
- Markdown digest
- Tests and linting

### Phase 1 - First LLM integration

- Add model provider abstraction
- Use LLM to classify relevance
- Use LLM to summarize articles
- Keep cost controls and dry-run mode

### Phase 2 - LangGraph agent

- Convert flow to LangGraph nodes
- Add state model
- Add retries and human-readable traces

### Phase 3 - Feedback and memory

- Add useful / not useful feedback
- Store feedback in SQLite
- Use feedback to improve relevance

### Phase 4 - RAG

- Build searchable history over articles and digests
- Ask questions over previous signals

### Phase 5 - Production

- Scheduled run
- Telegram/email delivery
- AWS deployment
- Observability
```
