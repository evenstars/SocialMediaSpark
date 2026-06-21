"""Node 2: generate/enhance — produce candidates from base photos + identity.

v1 stub uses all assets as references; a real impl would retrieve the best ones
via the vector store before generating.
"""
from __future__ import annotations

from studio.deps import Deps
from studio.state import JobState

N_CANDIDATES = 4


def generate(state: JobState, deps: Deps) -> dict:
    identity = state["identity"]
    refs = state.get("assets", [])
    n = state.get("n_candidates", N_CANDIDATES)
    candidates = deps.enhancer.generate(
        identity=identity,
        refs=refs,
        n=n,
        request=state.get("request", ""),
    )
    for c in candidates:
        deps.meta_store.save_candidate(c)
    log = state.get("log", []) + [f"generate: {len(candidates)} candidate(s)"]
    return {"candidates": candidates, "log": log}
