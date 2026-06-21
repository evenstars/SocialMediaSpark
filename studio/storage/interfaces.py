"""Storage abstract contracts.

Business code depends only on these interfaces. v1: SQLite + numpy + local files;
v2/cloud: Postgres(+pgvector) + object storage. Swapping impls needs no business changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from studio.state import Asset, Candidate


class MetadataStore(ABC):
    """Relational/metadata: assets, candidates, collections."""

    @abstractmethod
    def init_schema(self) -> None: ...

    @abstractmethod
    def save_asset(self, asset: Asset) -> None: ...

    @abstractmethod
    def save_candidate(self, candidate: Candidate) -> None: ...

    @abstractmethod
    def add_to_collection(self, collection: str, candidate_id: str) -> None: ...

    @abstractmethod
    def list_collection(self, collection: str) -> list[str]: ...


class VectorStore(ABC):
    """Store and similarity-search embeddings."""

    @abstractmethod
    def add(self, id: str, vec: np.ndarray) -> None: ...

    @abstractmethod
    def search(self, vec: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        """Return [(id, similarity)] sorted by similarity desc."""

    @abstractmethod
    def save(self) -> None: ...

    @abstractmethod
    def load(self) -> None: ...


class FileStore(ABC):
    """Store and fetch source photos / outputs."""

    @abstractmethod
    def put(self, data: bytes, name: str) -> str:
        """Write and return an accessible path/URL."""

    @abstractmethod
    def path(self, name: str) -> str: ...
