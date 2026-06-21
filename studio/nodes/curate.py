"""Node 5: curate — file into a usage collection and export (keep credentials).

M2: pass-through placeholder.
TODO(M3): write approved into collection, export file paths into exported.
"""
from __future__ import annotations

from studio.state import JobState


def curate(state: JobState) -> dict:
    log = state.get("log", []) + ["curate: (M3) file into collection + export"]
    return {"exported": state.get("exported", []), "log": log}
