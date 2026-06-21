"""Node 2: generate/enhance — retrieve base photos + call Enhancer for candidates.

M2: pass-through placeholder.
TODO(M3): retrieve base photos by request, call Enhancer.generate to produce candidates.
"""
from __future__ import annotations

from studio.state import JobState


def generate(state: JobState) -> dict:
    log = state.get("log", []) + ["generate: (M3) retrieve base photos + generate candidates"]
    return {"candidates": state.get("candidates", []), "log": log}
