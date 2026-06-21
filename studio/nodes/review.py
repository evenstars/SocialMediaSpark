"""Node 4: human review.

v1: auto-approve candidates that passed the gate, but keep needs_human=True so a
real reviewer (M6 Gradio UI) still has the final say.
"""
from __future__ import annotations

from studio.deps import Deps
from studio.state import JobState


def review(state: JobState, deps: Deps) -> dict:
    approved = []
    for c in state.get("candidates", []):
        c.status = "approved"
        c.needs_human = True
        deps.meta_store.save_candidate(c)
        approved.append(c)
    log = state.get("log", []) + [f"review: {len(approved)} auto-approved (await human)"]
    return {"approved": approved, "log": log}
