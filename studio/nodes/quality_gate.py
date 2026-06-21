"""Node 3: authenticity & quality gate — score + filter + write content credentials.

M2: pass-through placeholder.
TODO(M3): score via Scorer, filter via guardrails.evaluate, attach_content_credentials to passers.
"""
from __future__ import annotations

from studio.state import JobState


def quality_gate(state: JobState) -> dict:
    log = state.get("log", []) + ["quality_gate: (M3) identity/naturalness/aesthetic gate + credentials"]
    return {"candidates": state.get("candidates", []), "log": log}
