"""Node 5: curate — file approved outputs into a usage collection and export.

Export keeps content credentials (we never strip them).
"""
from __future__ import annotations

from studio.deps import Deps
from studio.state import JobState


def curate(state: JobState, deps: Deps) -> dict:
    collection = state.get("collection") or "default"
    exported = []
    for c in state.get("approved", []):
        deps.meta_store.add_to_collection(collection, c.id)
        exported.append(c.path)
    log = state.get("log", []) + [
        f"curate: {len(exported)} exported to collection '{collection}'"
    ]
    return {"collection": collection, "exported": exported, "log": log}
