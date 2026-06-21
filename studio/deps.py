"""Dependency container: the pluggable services nodes use.

Nodes never construct models/stores directly — they receive a Deps object.
This makes implementations swappable (stub <-> API <-> cloud) and tests easy
(inject fakes / a temp data dir).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import config
from studio.models.interfaces import Enhancer, FaceEmbedder, Scorer, Tagger
from studio.models.stubs import StubEnhancer, StubFaceEmbedder, StubScorer, StubTagger
from studio.storage.interfaces import FileStore, MetadataStore, VectorStore
from studio.storage.local_files import LocalFileStore
from studio.storage.numpy_vectors import NumpyVectorStore
from studio.storage.sqlite_store import SqliteMetadataStore


@dataclass
class Deps:
    tagger: Tagger
    embedder: FaceEmbedder
    enhancer: Enhancer
    scorer: Scorer
    meta_store: MetadataStore
    vector_store: VectorStore
    file_store: FileStore


def default_deps(data_dir: Optional[str | Path] = None) -> Deps:
    """Wire stub models + local stores. v1 default; M5 swaps enhancer/embedder."""
    base = Path(data_dir) if data_dir else config.DATA_DIR
    base.mkdir(parents=True, exist_ok=True)

    file_store = LocalFileStore(base / "files")
    embedder = StubFaceEmbedder()
    return Deps(
        tagger=StubTagger(),
        embedder=embedder,
        enhancer=StubEnhancer(file_store),
        scorer=StubScorer(),
        meta_store=SqliteMetadataStore(base / "library.db"),
        vector_store=NumpyVectorStore(base / "vectors.npz"),
        file_store=file_store,
    )
