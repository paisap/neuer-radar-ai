from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from neuer_radar.core.run_trace import RunTrace


def save_run_trace(trace: RunTrace, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(trace)
    data["started_at"] = trace.started_at.isoformat()

    if trace.finished_at is not None:
        data["finished_at"] = trace.finished_at.isoformat()

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
