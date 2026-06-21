"""Abstract contracts for model capabilities.

Business/nodes depend only on these interfaces; concrete impls (stub / OpenAI API /
self-hosted) are swappable without affecting each other.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from studio.state import Asset, Candidate


class Tagger(ABC):
    """Image -> structured tags (angle / lighting / scene / expression / quality...)."""

    @abstractmethod
    def tag(self, image_path: str) -> dict: ...


class FaceEmbedder(ABC):
    """Image -> face vector (embedding). Shared by identity reference and gate checks."""

    @abstractmethod
    def embed(self, image_path: str) -> np.ndarray: ...


class Enhancer(ABC):
    """Base photos + identity vector -> candidate outputs.

    M3 = deterministic stub; M5 = hosted image API (e.g. OpenAI);
    v2 = self-hosted (SDXL+InstantID).
    """

    @abstractmethod
    def generate(
        self,
        identity: np.ndarray,
        refs: list[Asset],
        n: int,
        request: str,
    ) -> list[Candidate]: ...


class Scorer(ABC):
    """Candidate -> quality scores. Must return at least {'naturalness': float, 'aesthetic': float}."""

    @abstractmethod
    def score(self, candidate: Candidate) -> dict: ...
