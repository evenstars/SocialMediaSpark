"""Node 1: ingest — tag + build identity reference, write to the library.

M2: pass-through placeholder; only logs and initializes assets.
TODO(M3): tag via Tagger, build identity via FaceEmbedder, persist to
MetadataStore/VectorStore/FileStore.
"""
from __future__ import annotations

from studio.state import JobState


def ingest(state: JobState) -> dict:
    log = state.get("log", []) + ["ingest: (M3) tag + build identity reference"]
    # M2 placeholder: keep the assets field present; real fill-in is in M3
    return {"assets": state.get("assets", []), "log": log}
