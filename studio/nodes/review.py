"""Node 4: human review — v1 auto-pass + flag for human (M6 wires Gradio).

M2: pass-through placeholder.
TODO(M3): move gated candidates into approved, set needs_human flag.
"""
from __future__ import annotations

from studio.state import JobState


def review(state: JobState) -> dict:
    log = state.get("log", []) + ["review: (M3) auto-pass + flag for human confirm"]
    return {"approved": state.get("approved", []), "log": log}
