# Architecture

## MVP flow

```text
collect_all -> rank_articles -> save_scored_articles -> build_digest -> render_markdown
```

## Initial design principles

1. Local-first before cloud.
2. Useful before fancy.
3. Small steps before complex agents.
4. No model calls until the non-AI pipeline works.
5. Every phase must create something demonstrable.

## Future LangGraph nodes

- collect_sources
- score_relevance
- summarize_articles
- persist_results
- generate_digest
- request_feedback
- update_memory
