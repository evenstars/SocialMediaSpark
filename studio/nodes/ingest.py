"""Node 1: ingest — tag base photos, build identity reference, persist.

Reads state["base_paths"], writes assets + an aggregated identity vector.
"""
from __future__ import annotations

import uuid

import numpy as np

from studio.deps import Deps
from studio.state import Asset, JobState


def ingest(state: JobState, deps: Deps) -> dict:
    assets: list[Asset] = []
    vectors = []
    for path in state.get("base_paths", []):
        vec = deps.embedder.embed(path)
        asset = Asset(
            id=uuid.uuid4().hex[:12],
            path=path,
            tags=deps.tagger.tag(path),
            identity_vec=vec,
        )
        deps.meta_store.save_asset(asset)
        deps.vector_store.add(asset.id, vec)
        assets.append(asset)
        vectors.append(vec)

    # identity = normalized mean of base-photo vectors
    if vectors:
        mean = np.mean(np.stack(vectors), axis=0)
        norm = np.linalg.norm(mean)
        identity = mean / norm if norm else mean
    else:
        identity = np.zeros(0)

    deps.vector_store.save()
    log = state.get("log", []) + [f"ingest: {len(assets)} asset(s), identity built"]
    return {"assets": assets, "identity": identity, "log": log}
