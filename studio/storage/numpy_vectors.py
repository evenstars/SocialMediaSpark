"""numpy implementation of VectorStore (v1).

Vectors kept in memory (id -> vector), persisted to a single .npz file.
Cosine similarity computed in memory. Fine for v1 scale; swap for pgvector later.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from studio.storage.interfaces import VectorStore


class NumpyVectorStore(VectorStore):
    def __init__(self, path: str | Path):
        self.path = str(path)
        self._vecs: dict[str, np.ndarray] = {}

    def add(self, id: str, vec: np.ndarray) -> None:
        self._vecs[id] = np.asarray(vec, dtype=float)

    def search(self, vec: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        q = np.asarray(vec, dtype=float)
        qn = np.linalg.norm(q)
        scored: list[tuple[str, float]] = []
        for id_, v in self._vecs.items():
            vn = np.linalg.norm(v)
            sim = 0.0 if qn == 0 or vn == 0 else float(np.dot(q, v) / (qn * vn))
            scored.append((id_, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def save(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        if self._vecs:
            np.savez(self.path, ids=np.array(list(self._vecs.keys())),
                     vecs=np.stack(list(self._vecs.values())))

    def load(self) -> None:
        if not Path(self.path).exists():
            return
        data = np.load(self.path, allow_pickle=True)
        self._vecs = {str(i): v for i, v in zip(data["ids"], data["vecs"])}
